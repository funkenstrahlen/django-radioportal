import 'd3';

function showGraph(uri, elem, selector) {
  // format for parsing time stamps in json
  var format = d3.time.format("%Y-%m-%d %H:%M:%S");

  var container = d3.select(elem);
  // computed width of container
  var elemWidth = container.node().getBoundingClientRect().width;

  var margin = {top: 20, right: 30, bottom: 20, left: 40};
  var width = elemWidth - margin.left - margin.right;
  var height = elemWidth*1./2. - margin.top - margin.bottom;

  var x = d3.time.scale().range([0, width]);
  var y = d3.scale.linear().range([height, 0]);
  var color = d3.scale.category10();

  // axis display objects, ticksize of -height/-width is for grid
  var xAxis = d3.svg.axis()
      .scale(x)
      .orient("bottom")
      .innerTickSize(-height)
      .tickFormat(d3.time.format('%H:%M'));

  var yAxis = d3.svg.axis()
      .scale(y)
      .innerTickSize(-width)
      .orient("left");

  // transform data for stacking
  var stack = d3.layout.stack()
      .offset("zero")
      .values(function(d) { return d.values; })
      .x(function(d) { return d.date; })
      .y(function(d) { return d.listeners; });

  var interp = "basis";

  // filled areas
  var area = d3.svg.area()
      .interpolate(interp)
      .x(function(d) { return x(d.date); })
      .y0(function(d) { return y(d.y0); })
      .y1(function(d) { return y(d.y0 + d.y); });

  // emphasing line above area
  var line = d3.svg.line()
      .interpolate(interp)
      .x(function(d) { return x(d.date); })
      .y(function(d) { return y(d.y0 + d.y); });

  var svg = container.append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
    .append("g")
      .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

  // fetch data and build graph when received
  d3.json(uri, function(error, data) {
    if (error) throw error;

    // convert data and listeners to objects
    data.forEach(function(d) {
      d.date = format.parse(d.stamp);
      d.value = +d.listener;
    });

    // Create time buckets to sort data
    var intervalBounds = d3.extent(data, function(d) { return d.date; });
    var dt = +data[0]["dt"];

    var interval = d3.time.minutes(d3.time.minute.offset(intervalBounds[0],-dt), d3.time.minute.offset(intervalBounds[1], dt), dt);

    // group data by selector (mount or host) and time slot
    // sum up listeners in each time slot
    var nest = d3.nest()
      .key(selector)
      .key(function(d) { return interval[d3.bisectLeft(interval, d.date)]; })
      .rollup(function(d) {
          return d3.sum(d, function(d1) {return d1.value;})
      });

    var entries = nest.entries(data);

    // post process data: parse time once more, add missing datapoints as area/line dont like missing data points
    entries.forEach(function(d1){
      d1.values.forEach(function(d2){
        d2.date = d3.time.format.iso.parse(d2.key);
      });

      result = []
      for (d of interval) {
        v = d1.values.filter(function(d2) { return d2.date.getTime() == d.getTime(); });
        if (v.length > 0) {
          result.push({"date": v[0].date, "listeners": v[0].values});
        } else {
          result.push({"date": d, "listeners": 0});
        }
      }
      d1.values = result;
    });

    var layers = stack(entries);

    // update data/axis-mapping
    x.domain(d3.extent(interval));
    y.domain([0, d3.max(entries, function(d) { return d3.max(d.values, function(d2) { return d2.y0 + d2.y; })})]);

    // draw axis
    svg.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    svg.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
          .attr("transform", "rotate(-90)")
          .attr("y", 6)
          .attr("dy", ".71em")
          .style("text-anchor", "end")
          .text("Listener");

    // draw data
    var l = svg.selectAll(".layer").data(layers).enter();

    l.append("path")
        .attr("class", "layer")
        .attr("d", function(d) { return area(d.values); })
        .style("opacity", "0.8")
        .attr("fill", function(d, i) { return color(d.key); });

    l.append("path")
        .attr("class", "line")
        .attr("d", function(d) { return line(d.values); })
        .style("fill", "none")
        .style("stroke-width", "2px")
        .attr("stroke", function(d, i) { return color(d.key); });

    // draw legend
    var legend = container
      .append("div")
        .style('margin-left', margin.left+"px")
        .style('margin-right', margin.right+"px")
        .style('width', width+"px")
        .selectAll('.legend')
        .data(color.domain()).enter()
        .append('div')
          .style('display','inline-block')
          .style('margin','0.5em')
          .attr('class', 'legend');

    legend.append('div')
      .style('width', '1.2em')
      .style('height', '1.2em')
      .style('float', 'left')
      .style('margin-right', '0.5em')
      .style('background-color', color);

    legend.append('span')
      .text(function(d) { return d; });

  // mouse over stuff
  var focus = svg.append("g")
      .attr("class", "focus")
      .style("display", "none");

  var hover = focus.append("rect")
      .attr("height", height)
      .attr("class", "hover")
      .attr("width", x(interval[1])-x(interval[0]))


  layers.forEach(function(l){
    l.text = focus.append("text")
      .attr("x", hover.attr("width"))
      .attr("dy", ".35em");
  });

  svg.append("rect")
      .attr("class", "overlay")
      .attr("width", width)
      .attr("height", height)
      .on("mouseover", function() { focus.style("display", null); })
      .on("mouseout", function() { focus.style("display", "none"); })
      .on("mousemove", mousemove);

  function mousemove() {
    var x0 = x.invert(d3.mouse(this)[0]),
        i = d3.bisectLeft(interval, x0, 1),
        d0 = interval[i - 1];

    focus.attr("transform", "translate(" + x(d0) + ",0)");

    layers.forEach(function(l){
      d = d3.bisector(function(d){ return d.date; }).left(l.values, x0);
      d = l.values[d];
      if (d.y == 0) return;
      var cy = d.y0 + d.y;
      if (d.y < 10 )
        cy += 10;
      l.text.attr("transform", "translate(0, "+ y(cy) +")").text(d.listeners);
    });
  }
  });
};

export default showGraph;
