<<<<<<< HEAD
# modal-streamlit-chat

First, create a `.streamlit/secrets.toml` file such that:

```toml
# fill in <your value>
DSBA_LLAMA3_KEY="<your key>"
MODAL_BASE_URL="https://<your url>--vllm-openai-compatible-serve.modal.run"
```

# To run locally:

```bash
$ python3.11 -m venv venv
$ source venv/bin/activate
$ python -m pip install -r requirements.txt
$ python -m streamlit run app.py
```
```bash windows
$ python -m venv venv
$ source venv/Scripts/activate
$ python -m pip install -r requirements.txt
$ python -m streamlit run app.py

```
# To run on modal:

Make sure you have a [Modal account](https://modal.com/). 

First, sign in:

```bash
# sign in
$ python -m modal setup
```

Then set Modal secrets first as `dsba-llama3-key` with the secret name `DSBA_LLAMA3_KEY` and `modal-base-url` as `MODAL_BASE_URL` which is your LLM serving endpoint (not including `v1/`).

You can run a temporary "dev" environment to test:

```bash
# to test
$ modal serve modal/serve_streamlit.py
```

Or deploy it as a new app to modal:

```bash
# when ready to deploy
$ modal deploy modal/serve_streamlit.py
```

=======
# los-tres-amigos
Group 2

[Google Drive](https://drive.google.com/drive/folders/1xqffRnx4d50VgeSR3pDII54lsyZi6U1Y?usp=drive_link)
>>>>>>> c298293e307da1a53076735716212dfd4436463a
