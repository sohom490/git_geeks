"""app.py - one-page web interface.   Run with:  streamlit run app.py"""
from datetime import datetime
from pathlib import Path

import streamlit as st

from matcher import analyze

LOG_PATH = Path(__file__).with_name("unmatched_log.txt")

st.set_page_config(page_title="Python Error Helper", page_icon="🐞")
st.title("🐞 Python Error Helper")
st.caption("Paste a Python error and get the likely causes and a suggested fix.")

error_text = st.text_area(
    "Paste your error here",
    height=240,
    placeholder='Traceback (most recent call last):\n  File "app.py", line 3, in <module>\n    ...\nKeyError: \'name\'',
)

if st.button("Analyze", type="primary"):
    if not error_text.strip():
        st.warning("Please paste an error first.")
    else:
        result = analyze(error_text)
        parsed = result["parsed"]

        if result["matched"]:
            st.subheader(f"{parsed['error_type']}")
            st.write(result["summary"])

            if parsed["file"]:
                st.info(
                    f"Location: **{parsed['file']}**, line **{parsed['line']}**"
                    + (f", in `{parsed['function']}`" if parsed["function"] else "")
                )
            if parsed["code_line"]:
                st.code(parsed["code_line"], language="python")

            st.subheader("Possible causes")
            for i, cause in enumerate(result["causes"], 1):
                st.markdown(f"{i}. {cause}")

            st.subheader("Suggested fix")
            st.write(result["fix"])
            if result["example"]:
                st.code(result["example"], language="python")
        else:
            st.error(result["reason"])
            if parsed["error_type"]:
                st.write(f"Error type: **{parsed['error_type']}**")
                st.write(f"Message: `{parsed['message']}`")
                if parsed["file"]:
                    st.write(f"Location: {parsed['file']}, line {parsed['line']}")
            st.markdown(f"[Search this error online]({result['search_url']})")

            # Log unmatched errors so you know which rules to add next
            with open(LOG_PATH, "a", encoding="utf-8") as f:
                f.write(f"--- {datetime.now().isoformat(timespec='seconds')} ---\n")
                f.write(error_text.strip() + "\n\n")
