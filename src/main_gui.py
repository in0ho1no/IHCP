import glob
import os

import streamlit as st

from main import HCPInfo, convert_file2hcp_info_list

COL_NUM_MODULE = 2


def get_folder_path() -> str:
    # 入力を促す
    path_input = st.text_input("対象のフォルダを選択してください")

    # 入力チェック
    if not os.path.exists(path_input):
        st.error(f"右記パスは存在しません。: {path_input}")
        return ""

    if not os.path.isdir(path_input):
        st.error(f"右記パスはフォルダではありません。: {path_input}")
        return ""

    if not os.path.isabs(path_input):
        st.error(f"相対パスの指定はできません。: {path_input}")
        return ""

    if any(pattern in path_input for pattern in ["..", "./", ".\\"]):
        st.error(f"相対パスの指定はできません。: {path_input}")
        return ""

    # パスが更新されたら初期化する
    if ("selected_path" not in st.session_state) or (st.session_state.selected_path != path_input):
        st.session_state.selected_path = path_input
        st.session_state.selected_file = ""
        st.session_state.selected_module_hcp_text = ""
        st.session_state.selected_module_svg = ""

    return path_input


def create_file_button(path_folder: str) -> None:
    st.success(f"フォルダパス: {path_folder}")
    st.subheader("ファイル一覧")
    file_path_list = glob.glob(path_folder + "\\**\\*.hcp", recursive=True)

    for file_path in file_path_list:
        # 存在しないファイルは無視
        if not os.path.isfile(file_path):
            continue

        # 特定の拡張子以外は無視
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in [".hcp"]:
            continue

        # ボタン配置
        file_name = file_path.replace(path_folder, "")
        if st.button(f"{file_name}"):
            # 選択されたらファイルパスを保持する
            st.session_state.selected_file = file_path
            # モジュールの選択状態をクリア
            st.session_state.selected_module_hcp_text = ""
            st.session_state.selected_module_svg = ""


def read_file(path: str) -> list[HCPInfo]:
    hcp_info_list: list[HCPInfo] = []
    try:
        hcp_info_list = convert_file2hcp_info_list(path)
    except Exception as e:
        st.error(f"ファイルの読み込み中にエラーが発生しました: {e}")

    return hcp_info_list


def create_module_button(hcp_info_list: list[HCPInfo]) -> None:
    row = st.columns(COL_NUM_MODULE)
    module_name_list: list[str] = []
    # リスト内から順に配置
    for count, hcp_info in enumerate(hcp_info_list):
        org_name = hcp_info.name

        # モジュール名の重複回避
        module_name = org_name
        module_exist = True
        duplicate_index = 1
        while module_exist is True:
            if module_name not in module_name_list:
                module_name_list.append(module_name)
                module_exist = False
            else:
                module_name = f"{org_name}_{duplicate_index}"
                duplicate_index += 1

        # 列の左から順に配置
        with row[count % COL_NUM_MODULE]:
            # ボタンを配置
            if st.button(f"{module_name}"):
                st.session_state.selected_module_hcp_text = hcp_info.raw_text
                st.session_state.selected_module_svg = hcp_info.svg_img


def set_module_list() -> None:
    if "selected_file" in st.session_state:
        select_file = st.session_state.selected_file

        # 選択されたファイルの内容を表示
        if select_file:
            # ファイルの読み込み
            hcp_info_list = read_file(select_file)
            # モジュールごとにボタンを表示
            create_module_button(hcp_info_list)


def show_svg_image() -> None:
    if "selected_module_svg" in st.session_state:
        tab_img, tab_txt = st.tabs(["IMG", "TXT"])
        with tab_img:
            st.markdown(st.session_state.selected_module_svg, unsafe_allow_html=True)
        with tab_txt:
            st.write(st.session_state.selected_module_hcp_text)


def main() -> None:
    st.title("HCPLens")

    # フォルダパスの取得
    folder_path = get_folder_path()
    if folder_path == "":
        return

    # ファイルごとにボタンを表示
    with st.sidebar:
        create_file_button(folder_path)

    st.divider()

    # モジュール一覧を表示
    with st.container(height=150):
        set_module_list()

    # SVG画像を表示する
    show_svg_image()


if __name__ == "__main__":
    main()
