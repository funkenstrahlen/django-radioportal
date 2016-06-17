import npm from "rollup-plugin-node-resolve";

export default {
  entry: "index.js",
  format: "umd",
  moduleName: "showgraph",
  plugins: [npm({jsnext: true})],
  dest: "showgraph.js",
  useStrict: false,
};
