import glob
import os

import streamlit as st

from main import HCPInfo, convert_file2hcp_info_list

PATH_DEFAULT = ""

COL_NUM_MODULE = 2
CONTAINER_HEIGHT_MODULES = 140


def set_input_folder_path_section() -> None:
    if "selected_path" not in st.session_state:
        st.session_state.selected_path = PATH_DEFAULT

    # フォルダパスの取得
    folder_path = get_folder_path()

    # パスが更新されたら初期化する
    if st.session_state.selected_path != folder_path:
        st.session_state.selected_path = folder_path
        st.session_state.selected_file = ""
        st.session_state.selected_module_hcp_text = ""
        st.session_state.selected_module_svg = ""


def get_folder_path() -> str:
    # 入力を促す
    path_input = st.text_input("対象のフォルダを選択してください")

    # 入力チェック
    if not os.path.exists(path_input):
        st.error(f"右記パスは存在しません。: {path_input}")
        return PATH_DEFAULT

    if not os.path.isdir(path_input):
        st.error(f"右記パスはフォルダではありません。: {path_input}")
        return PATH_DEFAULT

    if not os.path.isabs(path_input):
        st.error(f"相対パスの指定はできません。: {path_input}")
        return PATH_DEFAULT

    if any(pattern in path_input for pattern in ["..", "./", ".\\"]):
        st.error(f"相対パスの指定はできません。: {path_input}")
        return PATH_DEFAULT

    # 問題なければパスを返す
    return path_input


def set_file_button_section() -> None:
    # フォルダパスが未指定なら何もしない
    if "selected_path" not in st.session_state:
        return
    if st.session_state.selected_path == PATH_DEFAULT:
        return

    with st.sidebar:
        create_file_button(st.session_state.selected_path)


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


def set_module_list_section() -> None:
    # ファイル未選択なら何もしない
    if "selected_file" not in st.session_state:
        return
    if st.session_state.selected_file == "":
        return

    st.divider()

    with st.container(height=CONTAINER_HEIGHT_MODULES):
        set_module_list()


def set_module_list() -> None:
    # 選択されたファイルの内容を表示
    select_file = st.session_state.selected_file
    if select_file:
        st.write(f"{select_file}")
        # ファイルの読み込み
        hcp_info_list = read_file(select_file)
        # モジュールごとにボタンを表示
        create_module_button(hcp_info_list)


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
                st.session_state.selected_module_name = module_name
                st.session_state.selected_module_hcp_text = hcp_info.raw_text
                st.session_state.selected_module_svg = hcp_info.svg_img


def show_svg_image() -> None:
    # モジュール未選択なら何もしない
    if "selected_module_svg" not in st.session_state:
        return
    if st.session_state.selected_module_svg == "":
        return

    tab_img, tab_txt = st.tabs(["IMG", "TXT"])
    with tab_img:
        st.markdown(st.session_state.selected_module_svg, unsafe_allow_html=True)
    with tab_txt:
        st.write(st.session_state.selected_module_hcp_text)


def set_save_button_section() -> None:
    if "selected_module_svg" not in st.session_state:
        return
    if st.session_state.selected_module_svg == "":
        return

    st.divider()

    create_save_button()


def create_save_button() -> None:
    st.write("IMGを入力フォルダ内に保存します")
    if st.button("SVG画像として保存"):
        basepath = st.session_state.selected_file.split(".")[0]
        savepath = f"{basepath}_{st.session_state.selected_module_name}.svg"
        with open(savepath, "w", encoding="utf-8") as f:
            f.write(st.session_state.selected_module_svg)

        st.success(f"保存成功: {savepath}")


def main() -> None:
    st.title("IHCP")

    # フォルダパスの取得
    set_input_folder_path_section()

    # ファイルごとにボタンを表示
    set_file_button_section()

    # モジュール一覧を表示
    set_module_list_section()

    # SVG画像を表示する
    show_svg_image()

    # 保存ボタンを用意する
    set_save_button_section()


if __name__ == "__main__":
    main()
