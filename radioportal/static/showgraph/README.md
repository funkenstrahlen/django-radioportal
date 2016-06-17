This is a demonstration of building a custom D3 4.0 bundle using ES2015 modules and [Rollup](http://rollupjs.org). Custom bundles can be optimized to contain only the code you need. This example exposes just three fields on the `d3` object: [d3.event](https://github.com/d3/d3-selection#event), [d3.select](https://github.com/d3/d3-selection#select) and [d3.selectAll](https://github.com/d3/d3-selection#selectAll). The minified and gzipped bundle is only 3,691 bytes, a savings of 93% over the default build!

To build:

```
npm install
npm run prepublish
```

You may also run Rollup and UglifyJS directly:

```
rollup -c && uglifyjs d3.js -c -m -o d3.min.js
```
