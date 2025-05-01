# This file assumes the project root is up two directories
import pathlib


def project_root():
    return pathlib.Path(__file__).resolve().parents[2]  # Up two directories


def resources():
    return project_root() / "resources"
