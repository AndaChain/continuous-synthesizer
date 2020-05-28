import os
import argparse
import configparser


def get_config(filename):
    """
    All settings are stored in an external text file.
    """
    config = configparser.ConfigParser()
    config.read(filename)
    return config


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
        required=False,
        default="options.cfg",
        help="path to program options file")
    parser.add_argument("-x", "--sizex", required=False)
    parser.add_argument("-y", "--sizey", required=False)
    parser.add_argument("-f", "--wildcard", required=False)
    parser.add_argument("-w", "--waveform", required=False)
    return parser



def get_options_from_config(config):
    options = {}
    config = config["DEFAULT"]
    options["waveform"] = config["waveform"]
    options["size_x"] = int(config["size_x"])
    options["size_y"] = int(config["size_y"])
    options["frequency_board"] = config["frequency_board"]
    options["bass_frequencies_filename"] = config["bass_frequencies_filename"]
    options["transition_size"] = float(config["transition_size"])
    options["transposition_factor"] = float(config["transposition_factor"])
    options["no_of_voices"] = int(config["no_of_voices"])
    options["attack_time"] = float(config["attack_time"])
    options["release_time"] = float(config["release_time"])
    options["decay_time"] = float(config["decay_time"])
    options["after_decay_level"] = float(config["after_decay_level"])
    options["bass_attack_time"] = float(config["bass_attack_time"])
    options["bass_release_time"] = float(config["bass_release_time"])
    options["bass_decay_time"] = float(config["bass_decay_time"])
    options["bass_after_decay_level"] = float(config["bass_after_decay_level"])
    options["wildcard_frequency"] = float(config["wildcard_frequency"])
    options["samplerate"] = int(config["samplerate"])
    options["volume"] = float(config["volume"])
    return options


def replace_options_from_command_line(options, args):
    if args["sizex"]:
        options["size_x"] = int(args["sizex"])
    if args["sizey"]:
        options["size_y"] = int(args["sizey"])
    if args["wildcard"]:
        options["wildcard_frequency"] = float(args["wildcard"])
    if args["waveform"]:
        options["waveform"] = args["waveform"]


def get_options():
    parser = get_parser()
    parsed_arguments = vars(parser.parse_args())
    filename = parsed_arguments["config"]
    config = get_config(filename)
    options = get_options_from_config(config)
    replace_options_from_command_line(options, parsed_arguments)
    options["no_of_bass_voices"] = 1
    return options
