import os

import streamlit as st

from main import convert_txt2svg


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
    files = sorted(os.listdir(path_folder))
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
                with open(file_path, encoding="utf-8") as f:
                    content = f.read()
                st.subheader(f"ファイル内容: {selected_file}")
                st.code(content)

                svg_code = convert_txt2svg(content)
                st.markdown(svg_code, unsafe_allow_html=True)

            except Exception as e:
                st.error(f"ファイルの読み込み中にエラーが発生しました: {e}")


if __name__ == "__main__":
    main()
