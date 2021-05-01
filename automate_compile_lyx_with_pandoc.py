import glob
import sys ,file_iterator, os, pickle, pathlib
from fix_resources_in_latex_file import fix_resources_in_latex_file

__version__ = 2.1
print("this is automate_compile_lyx_with_pandoc version {}".format(__version__))
file_compile_times_path = os.path.join(os.path.dirname(__file__),"last_compile_times.dat")


clean_flag = ["-cc","--clean-compile"]
not_recursive_flag = ["-nr","--not_recursive"]
keep_eps_files_flag = ["-keps","--keep_eps"]
go_one_up_flag = ["-gou","--go_one_up"]
preview_flag = ["-v","--view"]

help_flag = ["-h","--help"]
clear_memory_flag = ["--clear-memory"]


if sys.argv[1] in help_flag:
    print("this is automate_compile_lyx_with_pandoc version {}\n"
          "usage:\n"
          "python automate_compile_lyx_with_pandoc <out format> <root path> [options]\n"
          "root path: some path at which to start compiling. if a folder is specified than will run on all lyx files in folder and by default on all lyx files in subfolders.\n"
          "options:\n"
          "{}: clean compile. compile all. not only files that were changed.\n"
          "{}: don't run on subfolders. only on given folder.\n"
          "{}: don't purge .eps files. (by default this program deletes all .eps files under root.)\n"
          "{}: run on the dirname of the given path. (usefull for lyx shortcuts)\n"
          "{}: view final file\n"
          "for help run:\n python automate_compile_lyx_with_pandoc {}\n"
          "for clearing memory of lyx compilation times:\n python automate_compile_lyx_with_pandoc {}\n"
          "example usage:\n"
          "python automate_compile_lyx_with_pandoc html E:\Some_path\\to_lyx_file.lyx -cc -gou\n"
          "".format(__version__," or ".join(clean_flag)," or ".join(not_recursive_flag)," or ".join(keep_eps_files_flag)
                    ," or ".join(go_one_up_flag)," or ".join(preview_flag)," or ".join(help_flag)
                    ," or ".join(clear_memory_flag)))
    quit()

if sys.argv[1] in clear_memory_flag:
    os.remove(file_compile_times_path)
    quit()

b_run_clean = False
b_run_recursive = True
b_purge_eps = True
b_preview = False
root_path = sys.argv[2]
out_format = sys.argv[1]
if os.path.splitext(root_path)[1] == ".autocompilelyx":
    root_path = os.path.splitext(root_path)[0] + ".lyx"

if any([a in clean_flag for a in sys.argv]):
    b_run_clean = True
if any([a in not_recursive_flag for a in sys.argv]):
    b_run_recursive = False
if any([a in keep_eps_files_flag for a in sys.argv]):
    b_purge_eps = False
if any([a in go_one_up_flag for a in sys.argv]):
    root_path = os.path.dirname(root_path)
if any([a in preview_flag for a in sys.argv]):
    b_preview = True


# read last lyx file compile times:
try:
    if b_run_clean:
        raise Exception
    with open(file_compile_times_path,"rb") as f:
        file_compile_times = pickle.load(f)
except:
    print("couldn't find file_compile_times data file at path {}, will make a new one.".format(file_compile_times_path))
    file_compile_times = {} # dictionary of compilation times: file_compile_times[<path>] = <last compilation time of path>

def run_command(command):
    print(command)
    os.system(command)

def convert_lyx_file(lyx_file):
    target_latex_file = os.path.splitext(lyx_file)[0] + ".tex"
    target_final_file = os.path.splitext(lyx_file)[0] + "." + out_format

    last_edit_time = pathlib.Path(lyx_file).stat().st_mtime
    last_compile_time = file_compile_times.get(target_final_file,0)
    if last_edit_time <= last_compile_time and os.path.exists(target_final_file):
        return

    # export latex
    run_command("start /wait lyx --export latex \"{}\"".format(lyx_file))

    # fix latex
    fix_resources_in_latex_file(target_latex_file)

    # maybe add css file
    add_css_file = ""
    if out_format == "html":
        local_css_file = os.path.splitext(target_latex_file)[0] + ".css"
        default_css_file = os.path.join(os.path.dirname(__file__), "default_style.css")
        if os.path.isfile(local_css_file):
            add_css_file = "-s -c \"{}\" ".format(local_css_file)
        elif os.path.isfile(default_css_file):
            add_css_file = "-s -c \"{}\" ".format(default_css_file)

    # convert with pandoc
    temp = os.getcwd()
    os.chdir(os.path.dirname(target_latex_file))
    run_command("pandoc -f latex -t {} {}\"{}\" -o \"{}\" --mathjax --wrap=none".format(out_format,add_css_file,target_latex_file,target_final_file))
    os.chdir(temp)

    # update file_compile_times
    file_compile_times[target_final_file] = pathlib.Path(target_final_file).stat().st_mtime


file_iterator.run(convert_lyx_file, root_path=root_path, b_recursive=b_run_recursive, files_filter="*.lyx")

# this will remove the ".eps" files
if b_purge_eps:
    if os.path.isfile(root_path):
        file_iterator.run(os.remove, root_path=os.path.dirname(root_path), b_recursive=b_run_recursive,
                          files_filter="*.eps")
    else:
        file_iterator.run(os.remove, root_path=root_path, b_recursive=b_run_recursive, files_filter="*.eps")

with open(file_compile_times_path, "wb") as f:
    pickle.dump(file_compile_times,f)

if b_preview:
    run_command("\"{}.{}\"".format(os.path.splitext(sys.argv[2])[0],out_format))

