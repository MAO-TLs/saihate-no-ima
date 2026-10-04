export const readerCategoryId = id => id === 'entries' ? 'hyperlinks' : id;

// Group image destinations for browsing without changing their canonical refs.
export function readerCategories(routes) {
  const images = routes.find(route => route.id === 'entries');
  return routes.filter(route => route.id === 'story' || route.id === 'hyperlinks').map(route => ({
    ...route,
    lineCount: route.lineCount + (route.id === 'hyperlinks' ? images?.lineCount ?? 0 : 0),
    scripts: [route, ...(route.id === 'hyperlinks' && images ? [images] : [])]
      .flatMap(source => source.scripts.map(script => ({...script, routeId: source.id, imageOnly: source.id === 'entries'}))),
  }));
}
