from asyncio import create_subprocess_exec
import json, os, argparse

def save_json(json_dict, fname):
    with open(fname, "w") as f:
        json.dump(json_dict, f, indent=4)

def load_json(fname):
    with open(fname, "r") as f:
        json_dict = json.load(f)
    return json_dict

def check(result_file, task_type):
    results = load_json(result_file)
    c_results = {'avg': {'total': 0, 'correct': 0}}
    for r in results['logs']:
        dim = r['doc']['dim']
        if dim not in c_results:
            c_results[dim] = {'total': 0, 'correct': 0}
        
        c_results[dim]['total'] += 1
        c_results[dim]['correct'] += r['avg_accuracy']['rating']
        c_results['avg']['total'] += 1
        c_results['avg']['correct'] += r['avg_accuracy']['rating']
    print('-'*100)
    print(task_type)
    for dim in c_results:
        print(dim, f"{c_results[dim]['correct']/c_results[dim]['total']*100:.2f}", f"{c_results[dim]['correct']}/{c_results[dim]['total']}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--result_path", type=str, default="lmms_eval_outputs", help="the folder containing lmms_eval outputs")
    args = parser.parse_args()

    rfiles = [f for f in os.listdir(args.result_path) if f.endswith('.json') and f.startswith('tempcompass')]
    for rfile in rfiles:
        task_type = rfile.replace('.json', '').replace('tempcompass_', '')
        check(os.path.join(args.result_path, rfile), task_type)
