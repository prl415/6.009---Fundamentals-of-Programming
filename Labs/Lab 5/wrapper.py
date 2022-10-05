import lab, json, traceback

def convert_to_tuples(input_data):
  input_data["start"] = tuple(input_data["start"])
  input_data["end"] = tuple(input_data["end"])
  input_data["graph"] = [{key:tuple(coord) for key, coord in edge.items()} for edge in input_data["graph"]]

def run_test(input_data):
  result = ""
  try:
      f = getattr(lab, input_data["function"])
      result = f(**input_data["inputs"])
  except:
    result = traceback.format_exc()
  return result

def shortest_path( input_data ):
  convert_to_tuples(input_data)
  return lab.shortest_path(input_data["graph"], input_data["start"], input_data["end"])

def shortest_path_no_lefts( input_data ):
  convert_to_tuples(input_data)
  return lab.shortest_path_no_lefts(input_data["graph"], input_data["start"], input_data["end"])

def shortest_path_k_lefts( input_data ):
  convert_to_tuples(input_data)
  return lab.shortest_path_k_lefts(input_data["graph"], input_data["start"], input_data["end"], input_data["k"])
