import gradio as gr
import torch
from modules.speaker import Speaker
from modules.utils.SeedContext import SeedContext
from modules.hf import spaces
from modules.models import load_chat_tts
from modules.utils.rng import np_rng
from modules.webui import webui_config
from modules.webui.webui_utils import get_speakers, tts_generate

import tempfile

names_list = [
    "Alice",
    "Bob",
    "Carol",
    "Carlos",
    "Charlie",
    "Chuck",
    "Chad",
    "Craig",
    "Dan",
    "Dave",
    "David",
    "Erin",
    "Eve",
    "Yves",
    "Faythe",
    "Frank",
    "Grace",
    "Heidi",
    "Ivan",
    "Judy",
    "Mallory",
    "Mallet",
    "Darth",
    "Michael",
    "Mike",
    "Niaj",
    "Olivia",
    "Oscar",
    "Peggy",
    "Pat",
    "Rupert",
    "Sybil",
    "Trent",
    "Ted",
    "Trudy",
    "Victor",
    "Vanna",
    "Walter",
    "Wendy",
]


@torch.inference_mode()
@spaces.GPU
def create_spk_from_seed(
    seed: int,
    name: str,
    gender: str,
    desc: str,
):
    chat_tts = load_chat_tts()
    with SeedContext(seed, True):
        emb = chat_tts.sample_random_speaker()
    spk = Speaker(seed=-2, name=name, gender=gender, describe=desc)
    spk.emb = emb

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pt") as tmp_file:
        torch.save(spk, tmp_file)
        tmp_file_path = tmp_file.name

    return tmp_file_path


@torch.inference_mode()
@spaces.GPU
def test_spk_voice(seed: int, text: str):
    return tts_generate(
        spk=seed,
        text=text,
    )


def random_speaker():
    seed = np_rng()
    name = names_list[seed % len(names_list)]
    return seed, name


def speaker_creator_ui():
    def on_generate(seed, name, gender, desc):
        file_path = create_spk_from_seed(seed, name, gender, desc)
        return file_path

    def create_test_voice_card(seed_input):
        with gr.Group():
            gr.Markdown("🎤Test voice")
            with gr.Row():
                test_voice_btn = gr.Button("Test Voice", variant="secondary")

                with gr.Column(scale=4):
                    test_text = gr.Textbox(
                        label="Test Text",
                        placeholder="Please input test text",
                        value=webui_config.localization.DEFAULT_SPEAKER_TEST_TEXT,
                    )
                    with gr.Row():
                        current_seed = gr.Label(label="Current Seed", value=-1)
                        with gr.Column(scale=4):
                            output_audio = gr.Audio(label="Output Audio", format="mp3")

        test_voice_btn.click(
            fn=test_spk_voice,
            inputs=[seed_input, test_text],
            outputs=[output_audio],
        )
        test_voice_btn.click(
            fn=lambda x: x,
            inputs=[seed_input],
            outputs=[current_seed],
        )

    gr.Markdown("SPEAKER_CREATOR_GUIDE")

    with gr.Row():
        with gr.Column(scale=2):
            with gr.Group():
                gr.Markdown("ℹ️Speaker info")
                seed_input = gr.Number(label="Seed", value=2)
                name_input = gr.Textbox(
                    label="Name", placeholder="Enter speaker name", value="Bob"
                )
                gender_input = gr.Textbox(
                    label="Gender", placeholder="Enter gender", value="*"
                )
                desc_input = gr.Textbox(
                    label="Description",
                    placeholder="Enter description",
                )
                random_button = gr.Button("Random Speaker")
            with gr.Group():
                gr.Markdown("🔊Generate speaker.pt")
                generate_button = gr.Button("Save .pt file")
                output_file = gr.File(label="Save to File")
        with gr.Column(scale=5):
            create_test_voice_card(seed_input=seed_input)
            create_test_voice_card(seed_input=seed_input)
            create_test_voice_card(seed_input=seed_input)
            create_test_voice_card(seed_input=seed_input)

    random_button.click(
        random_speaker,
        outputs=[seed_input, name_input],
    )

    generate_button.click(
        fn=on_generate,
        inputs=[seed_input, name_input, gender_input, desc_input],
        outputs=[output_file],
    )
