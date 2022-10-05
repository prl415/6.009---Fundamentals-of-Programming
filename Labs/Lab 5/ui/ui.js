"use strict";

var removedTestCases = ["5.in", "11.in"];

// RPC wrapper
function invoke_rpc(method, args, timeout, on_done) {
  $("#crash").hide();
  $("#timeout").hide();
  $("#rpc_spinner").show();
  //send RPC with whatever data is appropriate. Display an error message on crash or timeout
  var xhr = new XMLHttpRequest();
  xhr.open("POST", method, true);
  xhr.setRequestHeader("Content-Type", "application/json; charset=UTF-8");
  xhr.timeout = timeout;
  xhr.send(JSON.stringify(args));
  xhr.ontimeout = function() {
    $("#timeout").show();
    $("#rpc_spinner").hide();
    $("#crash").hide();
  };
  xhr.onloadend = function() {
    if (xhr.status === 200) {
      $("#rpc_spinner").hide();
      var result = JSON.parse(xhr.responseText);
      $("#timeout").hide();
      if (typeof on_done != "undefined") {
        on_done(result);
      }
    } else {
      $("#crash").show();
    }
  };
}

// Resource load wrapper
function load_resource(name, on_done) {
  var xhr = new XMLHttpRequest();
  xhr.open("GET", name, true);
  xhr.onloadend = function() {
    if (xhr.status === 200) {
      var result = JSON.parse(xhr.responseText);
      on_done(result);
    }
  };
  xhr.send();
}

// Code that runs first
$(document).ready(function() {
  // race condition if init() does RPC on function not yet registered by restart()!
  //restart();
  //init();
  invoke_rpc("/restart", {}, 0, function() {
    init();
  });
});

function restart() {
  invoke_rpc("/restart", {});
}

//  LAB CODE

function on_done(result) {
  // Show label
  $("#running").hide();
  $("#no_solution").hide();
  $("#crash").hide();
  $("#timeout").hide();

  solution = result;

  if (solution == null) {
    $("#no_solution").show();
  }

  render(state, solution);
}

function handle_solve() {
  $("#no_solution").hide();
  $("#crash").hide();
  $("#timeout").hide();
  $("#running").show();

  // Run student algorithm
  var args = {
    start: state.inputs.start,
    end: state.inputs.end,
    graph: state.inputs.graph,
    k: state.inputs.k
  };
  invoke_rpc("/" + state.function, args, 2000, on_done);
}

function handle_select(test_case) {
  // Hide labels
  $("#no_solution").hide();
  $("#crash").hide();
  $("#timeout").hide();

  // Set selection text
  $("#selection").text(test_case);

  // Clear solution
  solution = null;

  // Load test case
  var onloaded = function(result) {
    state = result;
    var width = state.width;
    var height = state.height;
    $("#selection").text(test_case + ": " + state.test);
    render(state);
  };

  load_resource("/cases/" + test_case, onloaded);
}

var state;
var solution = null;

function init() {
  var on_done_list_cases = function(result) {
    let v = result.sort(function(a, b) {
      return parseInt(parseInt(a.split(".")[0]) - parseInt(b.split(".")[0]));
    });
    for (var i in result) {
      if (!result[i].endsWith(".in")) {
        continue;
      }
      if (removedTestCases.includes(result[i])) {
        continue;
      }
      $("#options").append(
        '<li class="mdl-menu__item" onclick="handle_select(\'' + result[i] + "')\">" + result[i] + "</li>"
      );
    }
    handle_select(result[0]);
  };

  // List available files
  invoke_rpc("/ls", { path: "cases" }, 1000, on_done_list_cases);

  // Initialize SVG drawing
  draw = SVG("drawing");
  draw.viewbox(0, 0, 100, 100);
  draw.height = draw.width;
  SVG.on(window, "resize", function() {
    draw.spof();
  });
}

// Render logic
function render(state, solution) {
  clear_primitives();

  if (state == null) return;

  draw.viewbox(0, 0, state.width, state.height);
  draw.height = (draw.width * state.height) / state.width;

  // Draw grid
  for (var x = 0; x <= state.width; x++) {
    draw_line(x, 0, x, state.height).stroke({ width: 0.025, color: "#78909C" });
  }

  for (var y = 0; y <= state.height; y++) {
    draw_line(0, y, state.width, y).stroke({ width: 0.025, color: "#78909C" });
  }

  // Draw start and goal
  draw_rect()
    .move(state.inputs.start[0], state.inputs.start[1])
    .size(1, 1)
    .fill({ color: "#03A9F4", opacity: 0.5 });
  draw_rect()
    .move(state.inputs.end[0], state.inputs.end[1])
    .size(1, 1)
    .fill({ color: "#EF5350", opacity: 0.5 });

  // Draw graph embedded in the grid
  var graph = state.inputs.graph;
  for (var i = 1; i < graph.length; i++) {
    var edge = graph[i];
    //{"start":[1,0],"end":[2,0]},   {"start":[2,0],"end":[3,0]},
    draw_line(edge.start[0] + 0.5, edge.start[1] + 0.5, edge.end[0] + 0.5, edge.end[1] + 0.5).stroke({
      width: 0.1,
      color: "#B0BEC5",
      opacity: 1
    });
  }

  var path = [];

  // Draw result if it is available
  if (typeof solution === "undefined") {
    // there is no solution to work with
  } else {
    if (solution != null) {
      for (var i = 0; i < solution.length; i++) {
        var edge = solution[i];
        //{"start":[1,0],"end":[2,0]},   {"start":[2,0],"end":[3,0]},
        draw_line(edge.start[0] + 0.5, edge.start[1] + 0.5, edge.end[0] + 0.5, edge.end[1] + 0.5).stroke({
          width: 0.1,
          color: "#3F51B5",
          opacity: 1
        });
      }
    } else {
      draw_rect()
        .move(0.1, 0.1)
        .size(state.width - 0.2, state.height - 0.2)
        .fill({ color: "#F44336", opacity: 0.5 });
    }
  }

  // Hide remaining cached primitives
  render_primitives();
}

// Render back-end library
var draw;
var rectangle_cache = [];
var rectangle_counter = 0;
var line_cache = [];
var line_counter = 0;
var image_cache = [];

function clear_primitives() {
  rectangle_counter = 0;
  line_counter = 0;

  for (var i in image_cache) {
    image_cache[i].remove();
  }
}

function render_primitives() {
  while (rectangle_counter < rectangle_cache.length) {
    rectangle_cache[rectangle_counter].hide();
    rectangle_counter++;
  }
  while (line_counter < line_cache.length) {
    line_cache[line_counter].hide();
    line_counter++;
  }
}

function draw_rect() {
  if (rectangle_cache.length < rectangle_counter + 1) {
    rectangle_cache.push(draw.rect(1, 1));
  }
  rectangle_counter++;
  var r = rectangle_cache[rectangle_counter - 1];
  r.show();
  return r;
}

function draw_image(image) {
  var i = draw.image("/resources/" + image + ".svg", 100, 100);
  image_cache.push(i);
  return i;
}

function draw_line(x0, y0, x1, y1) {
  if (line_cache.length < line_counter + 1) {
    line_cache.push(draw.line(0, 0, 1, 1));
  }
  line_counter++;
  var l = line_cache[line_counter - 1];
  l.plot(x0, y0, x1, y1);
  l.show();
  return l;
}
