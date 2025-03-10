import glob
import os

import streamlit as st

from main import convert_file2svg_tuple_list


def get_folder_path() -> str:
    path_input = st.text_input("対象のフォルダを選択してください")

    if not os.path.exists(path_input):
        st.error(f"右記パスは存在しません。: {path_input}")
        return ""

    if not os.path.isdir(path_input):
        st.error(f"右記パスはフォルダではありません。: {path_input}")
        return ""

    st.success(f"フォルダパス: {path_input}")
    return path_input


def set_file_button(path_folder: str) -> None:
    st.subheader("ファイル一覧")
    flag_set = False
    files = glob.glob(path_folder + "\\**\\*.hcp", recursive=True)
    for file in files:
        # 存在しないファイルは無視
        file_path = os.path.join(path_folder, file)
        if not os.path.isfile(file_path):
            continue

        # 特定の拡張子以外は無視
        file_extension = os.path.splitext(file_path)[1].lower()
        if file_extension not in [".hcp"]:
            continue

        # ボタン配置
        if st.button(f"📄 {file}"):
            st.session_state.selected_file = file

        flag_set = True

    # 更新がない場合のみ、状態を初期化する
    if flag_set is False:
        st.error("フォルダ内に対象ファイルは存在しません。")
        st.session_state.selected_file = ""


def set_module_button(svg_tuple_list: list[tuple[str, str]]) -> None:
    st.subheader("モジュール一覧")
    flag_set = False

    for svg_tuple in svg_tuple_list:
        # ボタン配置
        if st.button(f"📄 {svg_tuple[0]}"):
            st.session_state.selected_module_svg = svg_tuple[1]
        flag_set = True

    # 更新がない場合のみ、状態を初期化する
    if flag_set is False:
        st.error("ファイル内にモジュールは存在しません。")
        st.session_state.selected_module_svg = ""


def main() -> None:
    st.title("HCPLens")

    # フォルダパスの取得
    folder_path = get_folder_path()
    if folder_path == "":
        return

    # ファイルごとにボタンを表示
    set_file_button(folder_path)

    st.write("---")

    # 選択されたファイルを表示
    if "selected_file" in st.session_state:
        selected_file = st.session_state.selected_file
        file_path = os.path.join(folder_path, selected_file)

        # 選択されたファイルの内容を表示
        if selected_file:
            try:
                svg_tuple_list = convert_file2svg_tuple_list(file_path)
            except Exception as e:
                st.error(f"ファイルの読み込み中にエラーが発生しました: {e}")

            # モジュールごとにボタンを表示
            set_module_button(svg_tuple_list)

            if "selected_module_svg" in st.session_state:
                st.subheader(f"ファイル内容: {selected_file}")
                st.markdown(st.session_state.selected_module_svg, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
