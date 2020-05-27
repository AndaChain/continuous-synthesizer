import os
# import argparse
# import configparser
# import misc_helpers
#
# def get_config(filename):
#     """
#     All settings are stored in an external text file.
#     """
#     config = configparser.ConfigParser()
#     config.read(filename)
#     return config
#
#
# def get_parser():
#     parser = argparse.ArgumentParser()
#     parser.add_argument("-c", "--config",
#         required=False,
#         default="options.cfg",
#         help="path to program options file")
#     parser.add_argument("-s", "--song",
#         required=False,
#         help="use this song instead of the one in the config file [don't write the extension .ly]")
#     parser.add_argument("-r", "--right",
#         required=False,
#         help="create song for the right hand [possible values: 0,1]")
#     parser.add_argument("-l", "--left",
#         required=False,
#         help="create song for the left hand [possible values: 0,1]")
#     parser.add_argument("-i", "--infolder",
#         required=False,
#         help="folder containing the lilypond files")
#     return parser
#
#
#
#
# def get_options_from_config(config):
#     true_strings = misc_helpers.get_true_strings()
#
#     options = {}
#     options["song"] = config["MAKE_OPTIONS"]["song"]
#     options["play_right"] = True if config["MAKE_OPTIONS"]["play_right"] in true_strings else False
#     options["play_left"] = True if config["MAKE_OPTIONS"]["play_left"] in true_strings else False
#     options["in_folder"] = misc_helpers.normalize_folder_string(config["MAKE_OPTIONS"]["in_folder"])
#     options["out_folder"] = misc_helpers.normalize_folder_string(config["MAKE_OPTIONS"]["out_folder"])
#     options["image_width"] = int(config["SHARED_OPTIONS"]["screen_width"])
#     options["image_height"] = int(config["SHARED_OPTIONS"]["screen_height"])
#     options["image_resolution"] = int(config["MAKE_OPTIONS"]["image_resolution"])
#     return options
#
#
# def replace_options_from_command_line(options, args):
#     true_strings = misc_helpers.get_true_strings()
#     if args["song"]:
#         options["song"] = args["song"]
#     if args["left"]:
#         options["play_left"] = True if args["left"] in true_strings else False
#
#
# def create_complete_paths(options):
#     hand_string = misc_helpers.get_folder_hand_string(options)
#     options["output_folder_complete"] = os.path.join(options["out_folder"], options["song"], hand_string) + "/"
#     options["lily_file"] = os.path.join(options["in_folder"], options["song"] + ".ly")
#
#
# def get_options():
#     parser = get_parser()
#     parsed_arguments = vars(parser.parse_args())
#     filename = parsed_arguments["config"]
#     config = get_config(filename)
#     options = get_options_from_config(config)
#
#
#     replace_options_from_command_line(options, parsed_arguments)
#     create_complete_paths(options)
#     options["staff_activations"] = [options["play_right"], options["play_left"]]
#
#     return options

def normalize_folder_string(folder):
    """
    Make sure that the folder names given in the input file
    contain / at the end.
    """
    folder = folder.strip()
    if folder[-1] == "/":
        return folder
    else:
        return folder + "/"



def get_options():
    options = {}
    #options["device"] = 0
    options["waveform"] = "square"
    options["waveform"] = "sine"
    options["waveform"] = "triangle"
    options["waveform"] = "sawtooth"
    options["size_x"] = 1333
    options["size_y"] = 733
    options["frequency_board"] = os.path.join("./frequency_boards/", "test.txt")
    options["transition_size"] = 0.8  # large value means big size
    options["transposition_factor"] = 1.0
    options["no_of_voices"] = 2
    options["attack_time"] = 0.95
    options["release_time"] = 0.94
    options["decay_time"] = 0.1
    options["after_decay_level"] = 1.0
    options["no_of_bass_voices"] = 1
    options["bass_attack_time"] = 0.8
    options["bass_release_time"] = 0.3
    options["bass_decay_time"] = 0.01
    options["bass_after_decay_level"] = 1.0
    options["wildcard_frequency"] = 90.0
    options["bass_frequencies_filename"] = os.path.join("./bass_frequencies/", "test.txt")

    # options[""] =
    return options
