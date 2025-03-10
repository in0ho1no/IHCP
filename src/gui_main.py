import os

import streamlit as st

from main import convert_txt2svg

st.title("特定フォルダのファイル一覧")

# 表示したいフォルダのパス
folder_path = r"./src/input/"

if os.path.exists(folder_path):
    files = sorted(os.listdir(folder_path))

    st.write("### ファイル一覧")

    # ファイルごとにボタンを表示
    for file in files:
        file_path = os.path.join(folder_path, file)
        if os.path.isfile(file_path):
            if st.button(f"📄 {file}"):
                st.session_state.selected_file = file

    # 選択されたファイルを表示
    if "selected_file" in st.session_state:
        selected_file = st.session_state.selected_file
        file_path = os.path.join(folder_path, selected_file)

        st.write("---")

        # 選択されたファイルの内容を表示
        if selected_file:
            file_path = os.path.join(folder_path, selected_file)
            try:
                # ファイルの種類に応じた表示方法
                file_extension = os.path.splitext(selected_file)[1].lower()

                # テキストファイルの場合
                if file_extension in [".hcp"]:
                    with open(file_path, encoding="utf-8") as f:
                        content = f.read()
                    st.subheader(f"ファイル内容: {selected_file}")
                    st.code(content)

                    svg_code = convert_txt2svg(content)
                    st.markdown(svg_code, unsafe_allow_html=True)

                # その他のファイル
                else:
                    st.warning(f"このファイル形式 ({file_extension}) の表示には対応していません。")

            except Exception as e:
                st.error(f"ファイルの読み込み中にエラーが発生しました: {e}")
