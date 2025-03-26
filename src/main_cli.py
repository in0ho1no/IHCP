import glob
from typing import NamedTuple

from core import HCPInfo, convert_file2hcp_info_list

INPUT_PATH = ".\\src\\input\\"
OUTPUT_PATH = ".\\src\\output\\"


class HCPFileInfo(NamedTuple):
    """hcpファイルに関する情報

    Attributes:
        name(str): HCPファイル名
        contents(list[HCPInfo]): HCPファイル内のモジュール毎の情報リスト
    """

    name: str
    contents: list[HCPInfo]


def get_hcp_files_info(folder_path: str) -> list[HCPFileInfo]:
    """フォルダ内のhcpファイルを読み込んでsvg画像とする情報を取得する

    Args:
        folder_path (str): 読み込むフォルダパス

    Returns:
        list[HCPInfo]: 読み込んだhcpファイルに関する情報のリスト
    """
    hcp_files_info: list[HCPFileInfo] = []
    for hcp_file_path in glob.glob(folder_path + "**\\*.hcp", recursive=True):
        hcp_files_info.append(
            HCPFileInfo(
                name=hcp_file_path,
                contents=convert_file2hcp_info_list(hcp_file_path),
            )
        )

    return hcp_files_info


def create_hcp_images(hcp_files_info: list[HCPFileInfo]) -> None:
    """hcpファイル内のmoduleごとにSVG画像を生成する

    Args:
        hcp_files_info (list[HCPFileInfo]): hcpファイル単位の情報から成るリスト
    """
    # ファイル単位で処理する
    for hcp_file_info in hcp_files_info:
        # 読み込んだファイルパスをそのまま出力ファイル名にする
        file_path = hcp_file_info.name.removeprefix(INPUT_PATH)
        basename = file_path.replace("\\", "_").split(".")[0]
        # ファイル内のモジュール単位で保存する
        for hcp_file_content in hcp_file_info.contents:
            output_module_svg = f"{OUTPUT_PATH}{basename}_{hcp_file_content.name}.svg"
            with open(output_module_svg, "w", encoding="utf-8") as f:
                f.write(hcp_file_content.svg_img)


def main() -> None:
    # フォルダからhcpファイルの情報を取得する
    hcp_files_info = get_hcp_files_info(INPUT_PATH)

    # hcpファイルの情報に基づいてsvg画像を生成する
    create_hcp_images(hcp_files_info)


if __name__ == "__main__":
    main()
