import tempfile

import matplotlib.pyplot as plt
from gig import Ent, EntType
from PIL import Image, ImageDraw, ImageFont
from utils import Log

log = Log("MapDecoderDrawMixin")


class MapDecoderDrawMixin:

    @staticmethod
    def generate_inspection_image(
        pil_image: Image.Image,
        reference_list: list[dict],
        color_reference_point: tuple[int, int, int],
    ) -> Image.Image:
        result_image = pil_image.copy()
        draw = ImageDraw.Draw(result_image)

        try:
            font = ImageFont.truetype("Arial.ttf", 12)
        except OSError:
            font = ImageFont.load_default()

        for ref in reference_list:
            label = ref.get("label", "")
            xy = ref.get("xy", (0, 0))
            latlng = ref.get("latlng", (0, 0))
            x, y = xy
            radius = 5
            draw.ellipse(
                [(x - radius, y - radius), (x + radius, y + radius)],
                fill=color_reference_point,
            )

            text = f"{label}\n{latlng}"
            draw.text((x + 8, y - 8), text, fill="black", font=font)

        return result_image

    @staticmethod
    def draw_map(
        ax: plt.Axes,
        map_ent_type: EntType,
        color_map_boundaries: tuple[int, int, int],
    ):

        ents = Ent.list_from_type(map_ent_type)
        for ent in ents:
            geo = ent.geo()
            geo.plot(
                ax=ax,
                facecolor="none",
                edgecolor=color_map_boundaries,
                linewidth=0.1,
            )

    @staticmethod
    def draw_legend(
        ax: plt.Axes,
        color_to_label: dict[tuple, str],
    ):
        import matplotlib.patches as mpatches

        patches = []
        for color, label in color_to_label.items():
            normalized_color = (
                color[0] / 255,
                color[1] / 255,
                color[2] / 255,
            )
            patch = mpatches.Patch(
                color=normalized_color,
                label=label,
            )
            patches.append(patch)

        ax.legend(
            handles=patches,
            loc="upper right",
            fontsize="small",
            framealpha=0.7,
        )

    @staticmethod
    def format_axes(ax):
        ax.grid(False)
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.set_xticks([])
        ax.set_yticks([])

    @staticmethod
    def generate_info_list_image(
        info_list: list[dict],
        color_map_boundaries: tuple[int, int, int],
        box_size_lat: int,
        map_ent_type: EntType,
        title: str,
        color_to_label: dict[tuple, str],
    ) -> Image.Image:
        plt.close()
        lats = [info["latlng"][0] for info in info_list]
        lngs = [info["latlng"][1] for info in info_list]
        colors = [
            (
                info["color"][0] / 255,
                info["color"][1] / 255,
                info["color"][2] / 255,
            )
            for info in info_list
        ]
        fig, ax = plt.subplots(figsize=(10, 10))
        MapDecoderDrawMixin.draw_map(
            ax=ax,
            map_ent_type=map_ent_type,
            color_map_boundaries=color_map_boundaries,
        )
        ax.scatter(
            lngs,
            lats,
            c=colors,
            s=200 * box_size_lat,
            marker="s",
        )
        MapDecoderDrawMixin.draw_legend(
            ax=ax,
            color_to_label=color_to_label,
        )
        plt.title(title)
        MapDecoderDrawMixin.format_axes(ax)

        temp_image_path = tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ).name
        plt.savefig(temp_image_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return Image.open(temp_image_path)

    @staticmethod
    def generate_image_for_ents(
        ent_to_label_to_n: dict,
        color_to_label: dict[tuple[int, int, int], str],
        map_ent_type: EntType,
        title: str,
    ) -> Image.Image:
        plt.close()
        fig, ax = plt.subplots(figsize=(10, 10))
        label_to_color = {
            label: color for color, label in color_to_label.items()
        }

        ents = Ent.list_from_type(map_ent_type)
        total_population = 0
        coloured_population = 0
        for ent in ents:
            population = ent.population
            total_population += population
            if ent.id in ent_to_label_to_n:
                coloured_population += population
                label_to_n = ent_to_label_to_n[ent.id]
                max_label = sorted(
                    label_to_n.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )[0][0]
                color_rgb = label_to_color[max_label]
                color = [c / 255 for c in color_rgb]

            else:
                color = "white"

            geo = ent.geo()

            geo.plot(
                ax=ax,
                facecolor=color,
                edgecolor="black",
                linewidth=0.1,
            )

        MapDecoderDrawMixin.format_axes(ax)
        plt.title(title)

        p_coloured = coloured_population / total_population
        n = len(ent_to_label_to_n)
        annotation_text = (
            f"{n} {map_ent_type.name}s,"
            + f" corresponding to {p_coloured:.1%}% of population"
        )
        ax.annotate(
            annotation_text,
            xy=(0.5, 0.98),
            xycoords="axes fraction",
            va="center",
            ha="center",
            fontsize="small",
        )

        temp_image_path = tempfile.NamedTemporaryFile(
            suffix=".png", delete=False
        ).name
        plt.savefig(temp_image_path, dpi=300, bbox_inches="tight")
        plt.close(fig)
        return Image.open(temp_image_path)
