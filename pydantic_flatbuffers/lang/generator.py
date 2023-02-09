from jinja2 import Environment, FileSystemLoader
from pydantic_flatbuffers.lang.datastructure import FileToGenerate
from typeguard import typechecked


def format_list(flist, pattern):
    return [pattern % s for s in flist]


@typechecked
def generate_files(*files_to_generate: FileToGenerate) -> None:
    for file_to_generate in files_to_generate:
        with open(file_to_generate.filename, "w") as target:
            env = Environment(
                loader=FileSystemLoader(file_to_generate.template.parent),
                trim_blocks=True,
                lstrip_blocks=True,
            )
            env.filters["format_list"] = format_list
            target.write(
                env.get_template(str(file_to_generate.template.name)).render(
                    file_to_generate.tree.__dict__
                )
            )
