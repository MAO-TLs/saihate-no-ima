import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
from unittest.mock import patch
import fix_movie_vbv as vbv
import movie_mpeg
import movie_install as installer
from movie_install_tests import MovieInstallTests

PACK=bytes.fromhex('000001ba2100010001800101')
END=bytes.fromhex('000001b9')
def header(value=3):
    fields=(800<<52)|(600<<40)|(1<<36)|(5<<32)|(0x3ffff<<14)|(1<<13)|(value<<3)
    return vbv.SEQUENCE_HEADER+fields.to_bytes(8,'big')
def pes(payload,stream=0xe0):
    return b'\0\0\1'+bytes([stream])+struct.pack('>H',len(payload)+1)+b'\x0f'+payload
def movie(value=3,tail=b'frame bytes'):
    return PACK+pes(header(value)+tail)+END

class HeaderTests(unittest.TestCase):
    def test_all_header_split_positions_and_audio_lookalikes(self):
        for split in range(1,12):
            a=header();audio=pes(header(9),0xc0)
            original=PACK+pes(a[:split])+audio+pes(a[split:]+b'picture')+END
            data=bytearray(original);self.assertEqual(vbv.patch_headers(data),[3])
            self.assertEqual(data,PACK+pes(header(112)[:split])+audio+pes(header(112)[split:]+b'picture')+END)
            self.assertEqual(vbv.patch_headers(data),[112])
            vbv.patch_headers(data,3);self.assertEqual(data,original)

    def test_finalize_future_renders_and_idempotence(self):
        original=movie()[:-4];after,proof=movie_mpeg.finalize(original)
        self.assertEqual(proof['vbv_before'],[3]);self.assertEqual(proof['vbv_after'],112)
        again,second=movie_mpeg.finalize(after);self.assertEqual(after,again)
        self.assertFalse(second['sequence_end_added']);self.assertFalse(second['program_end_added'])
        self.assertEqual(second['vbv_before'],[112])

    def test_reject_bad_or_incomplete_stream_without_partial_mutation(self):
        bad=[b'',PACK+pes(header()[:-1])+END,PACK+pes(header())+pes(header(),0xe1)+END,
             PACK+pes(header())+END+PACK,PACK+pes(header()[:-8]+b'\0'*8)+END,
             PACK+pes(header())+pes(b'\0\0\1\xb3')+END]
        for item in bad:
            data=bytearray(item)
            with self.assertRaises(ValueError):vbv.patch_headers(data)
            self.assertEqual(data,item)
        for n in range(1,12):
            with self.assertRaises(ValueError):vbv.patch_headers(bytearray(PACK[:n]))

    def test_standalone_report_backup_and_repeat(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'movie.bin';p.write_bytes(movie())
            vbv.repair(p);self.assertEqual(p.read_bytes(),movie())
            vbv.repair(p,True);self.assertEqual(p.read_bytes(),movie(112))
            backup=p.with_name(p.name+'.vbv-bak');self.assertEqual(backup.read_bytes(),movie())
            vbv.repair(p,True);self.assertEqual(backup.read_bytes(),movie())
            p.write_bytes(movie())
            with self.assertRaises(ValueError):vbv.repair(p,True)
            self.assertEqual(p.read_bytes(),movie())

class MovieRepairTests(MovieInstallTests):
    def setUp(self):
        super().setUp()
        self.outputs=[movie(tail=f'frame {n}'.encode()) for n in range(3)]
        for n,data in enumerate(self.outputs):
            (self.renders/f'mv{n:04d}.bin').write_bytes(data)
            self.receipt['movies'][n].update(sha256=hashlib.sha256(data).hexdigest(),size_bytes=len(data))
        self.write_receipt()

    def test_repair_verify_no_downgrade_restore_and_repeat(self):
        self.action('install');receipt=(self.renders/'movie-render-receipt.json').read_bytes()
        self.assertEqual(self.action('repair')['changed_files'],3)
        self.assertEqual(self.action('repair')['changed_files'],0)
        self.assertEqual(set(self.action('verify')['states'].values()),{'output-repaired'})
        self.assertEqual(self.action('install')['changed_files'],0)
        self.assertEqual((self.renders/'movie-render-receipt.json').read_bytes(),receipt)
        for n,data in enumerate(self.movie_bytes()):self.assertEqual(data,movie(112,f'frame {n}'.encode()))
        for n in range(3):(self.renders/f'mv{n:04d}.bin').unlink()
        self.action('verify');self.action('restore');self.assertEqual(self.movie_bytes(),self.sources)
        self.assert_sentinels()

    def test_repair_external_pr_patch_and_mixed_repaired_state(self):
        self.action('install');p=self.game/'HD/mv0001.bin';data=bytearray(p.read_bytes());vbv.patch_headers(data);p.write_bytes(data)
        self.assertEqual(self.action('verify')['states']['mv0001.bin'],'output-repaired')
        self.assertEqual(self.action('repair')['changed_files'],2)
        self.action('restore');self.assertEqual(self.movie_bytes(),self.sources)

    def test_repair_does_not_accept_unrelated_changes(self):
        self.action('install');p=self.game/'HD/mv0001.bin';data=bytearray(p.read_bytes());vbv.patch_headers(data);data[-5]^=1;p.write_bytes(data)
        before=self.movie_bytes()
        for action in ('verify','repair','restore'):
            with self.assertRaises(ValueError):self.action(action)
            self.assertEqual(self.movie_bytes(),before)

    def test_repair_failure_rolls_back_all_attempted_targets(self):
        self.action('install');real=installer.replace_from;calls=[]
        def fail(source,target,digest,backup):
            real(source,target,digest,backup);calls.append(target)
            if len(calls)==2:raise OSError('injected replacement failure')
        with patch.object(installer,'replace_from',side_effect=fail):
            with self.assertRaisesRegex(RuntimeError,r'rollback errors: \[\]'):self.action('repair')
        self.assertEqual(self.movie_bytes(),self.outputs);self.assert_sentinels()
        self.assertEqual(self.action('repair')['changed_files'],3)

    def test_repair_refuses_original_movies(self):
        with self.assertRaises(ValueError):self.action('repair')
        self.assertEqual(self.movie_bytes(),self.sources)

    def test_new_renderer_output_needs_no_repair(self):
        for n in range(3):
            data=movie(112,f'frame {n}'.encode());(self.renders/f'mv{n:04d}.bin').write_bytes(data)
            self.receipt['movies'][n]['sha256']=hashlib.sha256(data).hexdigest()
        self.write_receipt();self.action('install')
        self.assertEqual(self.action('repair')['changed_files'],0)
        self.assertEqual(set(self.action('verify')['states'].values()),{'output'})
        self.action('restore');self.assertEqual(self.movie_bytes(),self.sources)

if __name__=='__main__':unittest.main()
