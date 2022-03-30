import json
import os
import tempfile
import unittest
from difflib import SequenceMatcher

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import PIL
from test.test_data import media_data
import gradio as gr

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"


class TestTextbox(unittest.TestCase):
    def test_as_input_component(self):
        text_input = gr.Textbox()
        self.assertEqual(text_input.preprocess("Hello World!"), "Hello World!")
        self.assertEqual(text_input.preprocess_example("Hello World!"), "Hello World!")
        self.assertEqual(text_input.serialize("Hello World!", True), "Hello World!")
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = text_input.save_flagged(
                tmpdirname, "text_input", "Hello World!", None
            )
            self.assertEqual(to_save, "Hello World!")
            restored = text_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, "Hello World!")

        with self.assertWarns(DeprecationWarning):
            _ = gr.Textbox(type="number")

        self.assertEqual(
            text_input.tokenize("Hello World! Gradio speaking."),
            (
                ["Hello", "World!", "Gradio", "speaking."],
                [
                    "World! Gradio speaking.",
                    "Hello Gradio speaking.",
                    "Hello World! speaking.",
                    "Hello World! Gradio",
                ],
                None,
            ),
        )
        text_input.interpretation_replacement = "unknown"
        self.assertEqual(
            text_input.tokenize("Hello World! Gradio speaking."),
            (
                ["Hello", "World!", "Gradio", "speaking."],
                [
                    "unknown World! Gradio speaking.",
                    "Hello unknown Gradio speaking.",
                    "Hello World! unknown speaking.",
                    "Hello World! Gradio unknown",
                ],
                None,
            ),
        )

        self.assertIsInstance(text_input.generate_sample(), str)

    def test_in_interface_as_input(self):
        iface = gr.Interface(lambda x: x[::-1], "textbox", "textbox")
        self.assertEqual(iface.process(["Hello"])[0], ["olleH"])
        iface = gr.Interface(
            lambda sentence: max([len(word) for word in sentence.split()]),
            gr.Textbox(),
            "number",
            interpretation="default",
        )
        scores, alternative_outputs = iface.interpret(
            ["Return the length of the longest word in this sentence"]
        )
        self.assertEqual(
            scores,
            [
                [
                    ("Return", 0.0),
                    (" ", 0),
                    ("the", 0.0),
                    (" ", 0),
                    ("length", 0.0),
                    (" ", 0),
                    ("of", 0.0),
                    (" ", 0),
                    ("the", 0.0),
                    (" ", 0),
                    ("longest", 0.0),
                    (" ", 0),
                    ("word", 0.0),
                    (" ", 0),
                    ("in", 0.0),
                    (" ", 0),
                    ("this", 0.0),
                    (" ", 0),
                    ("sentence", 1.0),
                    (" ", 0),
                ]
            ],
        )
        self.assertEqual(
            alternative_outputs,
            [[[8], [8], [8], [8], [8], [8], [8], [8], [8], [7]]],
        )

    def test_in_interface_as_output(self):
        iface = gr.Interface(lambda x: x[-1], "textbox", gr.Textbox())
        self.assertEqual(iface.process(["Hello"])[0], ["o"])
        iface = gr.Interface(lambda x: x / 2, "number", gr.Textbox())
        self.assertEqual(iface.process([10])[0], ["5.0"])


class TestNumber(unittest.TestCase):
    def test_as_component(self):
        numeric_input = gr.Number()
        self.assertEqual(numeric_input.preprocess(3), 3.0)
        self.assertEqual(numeric_input.preprocess(None), None)
        self.assertEqual(numeric_input.preprocess_example(3), 3)
        self.assertEqual(numeric_input.serialize(3, True), 3)
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = numeric_input.save_flagged(tmpdirname, "numeric_input", 3, None)
            self.assertEqual(to_save, 3)
            restored = numeric_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, 3)
        self.assertIsInstance(numeric_input.generate_sample(), float)
        numeric_input.set_interpret_parameters(steps=3, delta=1, delta_type="absolute")
        self.assertEqual(
            numeric_input.get_interpretation_neighbors(1),
            ([-2.0, -1.0, 0.0, 2.0, 3.0, 4.0], {}),
        )
        numeric_input.set_interpret_parameters(steps=3, delta=1, delta_type="percent")
        self.assertEqual(
            numeric_input.get_interpretation_neighbors(1),
            ([0.97, 0.98, 0.99, 1.01, 1.02, 1.03], {}),
        )
        self.assertEqual(
            numeric_input.get_template_context(),
            {"default_value": None, "name": "number", "label": None, "css": {}},
        )

    def test_in_interface(self):
        iface = gr.Interface(lambda x: x**2, "number", "textbox")
        self.assertEqual(iface.process([2])[0], ["4.0"])
        iface = gr.Interface(
            lambda x: x**2, "number", "number", interpretation="default"
        )
        scores, alternative_outputs = iface.interpret([2])
        self.assertEqual(
            scores,
            [
                [
                    (1.94, -0.23640000000000017),
                    (1.96, -0.15840000000000032),
                    (1.98, -0.07960000000000012),
                    [2, None],
                    (2.02, 0.08040000000000003),
                    (2.04, 0.16159999999999997),
                    (2.06, 0.24359999999999982),
                ]
            ],
        )
        self.assertEqual(
            alternative_outputs,
            [
                [
                    [3.7636],
                    [3.8415999999999997],
                    [3.9204],
                    [4.0804],
                    [4.1616],
                    [4.2436],
                ]
            ],
        )


class TestSlider(unittest.TestCase):
    def test_as_component(self):
        slider_input = gr.Slider()
        self.assertEqual(slider_input.preprocess(3.0), 3.0)
        self.assertEqual(slider_input.preprocess_example(3), 3)
        self.assertEqual(slider_input.serialize(3, True), 3)
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = slider_input.save_flagged(tmpdirname, "slider_input", 3, None)
            self.assertEqual(to_save, 3)
            restored = slider_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, 3)

        self.assertIsInstance(slider_input.generate_sample(), int)
        slider_input = gr.Slider(
            default_value=15, minimum=10, maximum=20, step=1, label="Slide Your Input"
        )
        self.assertEqual(
            slider_input.get_template_context(),
            {
                "minimum": 10,
                "maximum": 20,
                "step": 1,
                "default_value": 15,
                "name": "slider",
                "label": "Slide Your Input",
                "css": {},
            },
        )

    def test_in_interface(self):
        iface = gr.Interface(lambda x: x**2, "slider", "textbox")
        self.assertEqual(iface.process([2])[0], ["4"])
        iface = gr.Interface(
            lambda x: x**2, "slider", "number", interpretation="default"
        )
        scores, alternative_outputs = iface.interpret([2])
        self.assertEqual(
            scores,
            [
                [
                    -4.0,
                    200.08163265306123,
                    812.3265306122449,
                    1832.7346938775513,
                    3261.3061224489797,
                    5098.040816326531,
                    7342.938775510205,
                    9996.0,
                ]
            ],
        )
        self.assertEqual(
            alternative_outputs,
            [
                [
                    [0.0],
                    [204.08163265306123],
                    [816.3265306122449],
                    [1836.7346938775513],
                    [3265.3061224489797],
                    [5102.040816326531],
                    [7346.938775510205],
                    [10000.0],
                ]
            ],
        )


class TestCheckbox(unittest.TestCase):
    def test_as_component(self):
        bool_input = gr.Checkbox()
        self.assertEqual(bool_input.preprocess(True), True)
        self.assertEqual(bool_input.preprocess_example(True), True)
        self.assertEqual(bool_input.serialize(True, True), True)
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = bool_input.save_flagged(tmpdirname, "bool_input", True, None)
            self.assertEqual(to_save, True)
            restored = bool_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, True)
        self.assertIsInstance(bool_input.generate_sample(), bool)
        bool_input = gr.Checkbox(default_value=True, label="Check Your Input")
        self.assertEqual(
            bool_input.get_template_context(),
            {
                "default_value": True,
                "name": "checkbox",
                "label": "Check Your Input",
                "css": {},
            },
        )

    def test_in_interface(self):
        iface = gr.Interface(lambda x: 1 if x else 0, "checkbox", "number")
        self.assertEqual(iface.process([True])[0], [1])
        iface = gr.Interface(
            lambda x: 1 if x else 0, "checkbox", "number", interpretation="default"
        )
        scores, alternative_outputs = iface.interpret([False])
        self.assertEqual(scores, [(None, 1.0)])
        self.assertEqual(alternative_outputs, [[[1]]])
        scores, alternative_outputs = iface.interpret([True])
        self.assertEqual(scores, [(-1.0, None)])
        self.assertEqual(alternative_outputs, [[[0]]])


class TestCheckboxGroup(unittest.TestCase):
    def test_as_component(self):
        checkboxes_input = gr.CheckboxGroup(["a", "b", "c"])
        self.assertEqual(checkboxes_input.preprocess(["a", "c"]), ["a", "c"])
        self.assertEqual(checkboxes_input.preprocess_example(["a", "c"]), ["a", "c"])
        self.assertEqual(checkboxes_input.serialize(["a", "c"], True), ["a", "c"])
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = checkboxes_input.save_flagged(
                tmpdirname, "checkboxes_input", ["a", "c"], None
            )
            self.assertEqual(to_save, '["a", "c"]')
            restored = checkboxes_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, ["a", "c"])
        self.assertIsInstance(checkboxes_input.generate_sample(), list)
        checkboxes_input = gr.CheckboxGroup(
            default_selected=["a", "c"],
            choices=["a", "b", "c"],
            label="Check Your Inputs",
        )
        self.assertEqual(
            checkboxes_input.get_template_context(),
            {
                "choices": ["a", "b", "c"],
                "default_value": ["a", "c"],
                "name": "checkboxgroup",
                "label": "Check Your Inputs",
                "css": {},
            },
        )
        with self.assertRaises(ValueError):
            wrong_type = gr.CheckboxGroup(["a"], type="unknown")
            wrong_type.preprocess(0)

    def test_in_interface(self):
        checkboxes_input = gr.CheckboxGroup(["a", "b", "c"])
        iface = gr.Interface(lambda x: "|".join(x), checkboxes_input, "textbox")
        self.assertEqual(iface.process([["a", "c"]])[0], ["a|c"])
        self.assertEqual(iface.process([[]])[0], [""])
        checkboxes_input = gr.CheckboxGroup(["a", "b", "c"], type="index")


class TestRadio(unittest.TestCase):
    def test_as_component(self):
        radio_input = gr.Radio(["a", "b", "c"])
        self.assertEqual(radio_input.preprocess("c"), "c")
        self.assertEqual(radio_input.preprocess_example("a"), "a")
        self.assertEqual(radio_input.serialize("a", True), "a")
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = radio_input.save_flagged(tmpdirname, "radio_input", "a", None)
            self.assertEqual(to_save, "a")
            restored = radio_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, "a")
        self.assertIsInstance(radio_input.generate_sample(), str)
        radio_input = gr.Radio(
            choices=["a", "b", "c"], default="a", label="Pick Your One Input"
        )
        self.assertEqual(
            radio_input.get_template_context(),
            {
                "choices": ["a", "b", "c"],
                "default_value": "a",
                "name": "radio",
                "label": "Pick Your One Input",
                "css": {},
            },
        )
        with self.assertRaises(ValueError):
            wrong_type = gr.Radio(["a", "b"], type="unknown")
            wrong_type.preprocess(0)

    def test_in_interface(self):
        radio_input = gr.Radio(["a", "b", "c"])
        iface = gr.Interface(lambda x: 2 * x, radio_input, "textbox")
        self.assertEqual(iface.process(["c"])[0], ["cc"])
        radio_input = gr.Radio(["a", "b", "c"], type="index")
        iface = gr.Interface(
            lambda x: 2 * x, radio_input, "number", interpretation="default"
        )
        self.assertEqual(iface.process(["c"])[0], [4])
        scores, alternative_outputs = iface.interpret(["b"])
        self.assertEqual(scores, [[-2.0, None, 2.0]])
        self.assertEqual(alternative_outputs, [[[0], [4]]])


class TestDropdown(unittest.TestCase):
    def test_as_component(self):
        dropdown_input = gr.Dropdown(["a", "b", "c"])
        self.assertEqual(dropdown_input.preprocess("c"), "c")
        self.assertEqual(dropdown_input.preprocess_example("a"), "a")
        self.assertEqual(dropdown_input.serialize("a", True), "a")
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = dropdown_input.save_flagged(
                tmpdirname, "dropdown_input", "a", None
            )
            self.assertEqual(to_save, "a")
            restored = dropdown_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, "a")
        self.assertIsInstance(dropdown_input.generate_sample(), str)
        dropdown_input = gr.Dropdown(
            choices=["a", "b", "c"], default="a", label="Drop Your Input"
        )
        self.assertEqual(
            dropdown_input.get_template_context(),
            {
                "choices": ["a", "b", "c"],
                "default_value": "a",
                "name": "dropdown",
                "label": "Drop Your Input",
                "css": {},
            },
        )
        with self.assertRaises(ValueError):
            wrong_type = gr.Dropdown(["a"], type="unknown")
            wrong_type.preprocess(0)

    def test_in_interface(self):
        dropdown_input = gr.Dropdown(["a", "b", "c"])
        iface = gr.Interface(lambda x: 2 * x, dropdown_input, "textbox")
        self.assertEqual(iface.process(["c"])[0], ["cc"])
        dropdown = gr.Dropdown(["a", "b", "c"], type="index")
        iface = gr.Interface(
            lambda x: 2 * x, dropdown, "number", interpretation="default"
        )
        self.assertEqual(iface.process(["c"])[0], [4])
        scores, alternative_outputs = iface.interpret(["b"])
        self.assertEqual(scores, [[-2.0, None, 2.0]])
        self.assertEqual(alternative_outputs, [[[0], [4]]])


class TestImage(unittest.TestCase):
    def test_as_component_as_input(self):
        img = media_data.BASE64_IMAGE
        image_input = gr.Image()
        self.assertEqual(image_input.preprocess(img).shape, (68, 61, 3))
        image_input = gr.Image(shape=(25, 25), image_mode="L")
        self.assertEqual(image_input.preprocess(img).shape, (25, 25))
        image_input = gr.Image(shape=(30, 10), type="pil")
        self.assertEqual(image_input.preprocess(img).size, (30, 10))
        self.assertEqual(image_input.preprocess_example("test/test_files/bus.png"), img)
        self.assertEqual(image_input.serialize("test/test_files/bus.png", True), img)
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = image_input.save_flagged(tmpdirname, "image_input", img, None)
            self.assertEqual("image_input/0.png", to_save)
            to_save = image_input.save_flagged(tmpdirname, "image_input", img, None)
            self.assertEqual("image_input/1.png", to_save)
            restored = image_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, "image_input/1.png")

        self.assertIsInstance(image_input.generate_sample(), str)
        image_input = gr.Image(
            source="upload", tool="editor", type="pil", label="Upload Your Image"
        )
        self.assertEqual(
            image_input.get_template_context(),
            {
                "image_mode": "RGB",
                "shape": None,
                "source": "upload",
                "tool": "editor",
                "name": "image",
                "label": "Upload Your Image",
                "css": {},
                "default_value": None,
            },
        )
        self.assertIsNone(image_input.preprocess(None))
        image_input = gr.Image(invert_colors=True)
        self.assertIsNotNone(image_input.preprocess(img))
        image_input.preprocess(img)
        with self.assertWarns(DeprecationWarning):
            file_image = gr.Image(type="file")
            file_image.preprocess(media_data.BASE64_IMAGE)
        file_image = gr.Image(type="filepath")
        self.assertIsInstance(file_image.preprocess(img), str)
        with self.assertRaises(ValueError):
            wrong_type = gr.Image(type="unknown")
            wrong_type.preprocess(img)
        with self.assertRaises(ValueError):
            wrong_type = gr.Image(type="unknown")
            wrong_type.serialize("test/test_files/bus.png", False)
        img_pil = PIL.Image.open("test/test_files/bus.png")
        image_input = gr.Image(type="numpy")
        self.assertIsInstance(image_input.serialize(img_pil, False), str)
        image_input = gr.Image(type="pil")
        self.assertIsInstance(image_input.serialize(img_pil, False), str)
        image_input = gr.Image(type="file")
        with open("test/test_files/bus.png") as f:
            self.assertEqual(image_input.serialize(f, False), img)
        image_input.shape = (30, 10)
        self.assertIsNotNone(image_input._segment_by_slic(img))

    def test_in_interface_as_input(self):
        img = media_data.BASE64_IMAGE
        image_input = gr.Image()
        iface = gr.Interface(
            lambda x: PIL.Image.open(x).rotate(90, expand=True),
            gr.Image(shape=(30, 10), type="file"),
            "image",
        )
        output = iface.process([img])[0][0]
        self.assertEqual(
            gr.processing_utils.decode_base64_to_image(output).size, (10, 30)
        )
        iface = gr.Interface(
            lambda x: np.sum(x), image_input, "number", interpretation="default"
        )
        scores, alternative_outputs = iface.interpret([img])
        self.assertEqual(scores, media_data.SUM_PIXELS_INTERPRETATION["scores"])
        self.assertEqual(
            alternative_outputs,
            media_data.SUM_PIXELS_INTERPRETATION["alternative_outputs"],
        )
        iface = gr.Interface(
            lambda x: np.sum(x), image_input, "label", interpretation="shap"
        )
        scores, alternative_outputs = iface.interpret([img])
        self.assertEqual(
            len(scores[0]),
            len(media_data.SUM_PIXELS_SHAP_INTERPRETATION["scores"][0]),
        )
        self.assertEqual(
            len(alternative_outputs[0]),
            len(media_data.SUM_PIXELS_SHAP_INTERPRETATION["alternative_outputs"][0]),
        )
        image_input = gr.Image(shape=(30, 10))
        iface = gr.Interface(
            lambda x: np.sum(x), image_input, "number", interpretation="default"
        )
        self.assertIsNotNone(iface.interpret([img]))

    def test_as_component_as_output(self):
        y_img = gr.processing_utils.decode_base64_to_image(media_data.BASE64_IMAGE)
        image_output = gr.Image()
        self.assertTrue(
            image_output.postprocess(y_img).startswith(
                "data:image/png;base64,iVBORw0KGgoAAA"
            )
        )
        self.assertTrue(
            image_output.postprocess(np.array(y_img)).startswith(
                "data:image/png;base64,iVBORw0KGgoAAA"
            )
        )
        with self.assertWarns(DeprecationWarning):
            plot_output = gr.Image(plot=True)

        xpoints = np.array([0, 6])
        ypoints = np.array([0, 250])
        fig = plt.figure()
        plt.plot(xpoints, ypoints)
        self.assertTrue(
            plot_output.postprocess(fig).startswith("data:image/png;base64,")
        )
        with self.assertRaises(ValueError):
            image_output.postprocess([1, 2, 3])
        image_output = gr.Image(type="numpy")
        self.assertTrue(
            image_output.postprocess(y_img).startswith("data:image/png;base64,")
        )
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = image_output.save_flagged(
                tmpdirname, "image_output", media_data.BASE64_IMAGE, None
            )
            self.assertEqual("image_output/0.png", to_save)
            to_save = image_output.save_flagged(
                tmpdirname, "image_output", media_data.BASE64_IMAGE, None
            )
            self.assertEqual("image_output/1.png", to_save)

    def test_in_interface_as_output(self):
        def generate_noise(width, height):
            return np.random.randint(0, 256, (width, height, 3))

        iface = gr.Interface(generate_noise, ["slider", "slider"], "image")
        self.assertTrue(
            iface.process([10, 20])[0][0].startswith("data:image/png;base64")
        )


class TestAudio(unittest.TestCase):
    def test_as_component_as_input(self):
        x_wav = media_data.BASE64_AUDIO
        audio_input = gr.Audio()
        output = audio_input.preprocess(x_wav)
        self.assertEqual(output[0], 8000)
        self.assertEqual(output[1].shape, (8046,))
        self.assertEqual(
            audio_input.serialize("test/test_files/audio_sample.wav", True)["data"],
            x_wav["data"],
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = audio_input.save_flagged(tmpdirname, "audio_input", x_wav, None)
            self.assertEqual("audio_input/0.wav", to_save)
            to_save = audio_input.save_flagged(tmpdirname, "audio_input", x_wav, None)
            self.assertEqual("audio_input/1.wav", to_save)
            restored = audio_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, "audio_input/1.wav")

        self.assertIsInstance(audio_input.generate_sample(), dict)
        audio_input = gr.Audio(label="Upload Your Audio")
        self.assertEqual(
            audio_input.get_template_context(),
            {
                "source": "upload",
                "name": "audio",
                "label": "Upload Your Audio",
                "css": {},
                "default_value": None,
            },
        )
        self.assertIsNone(audio_input.preprocess(None))
        x_wav["is_example"] = True
        x_wav["crop_min"], x_wav["crop_max"] = 1, 4
        self.assertIsNotNone(audio_input.preprocess(x_wav))
        with self.assertWarns(DeprecationWarning):
            audio_input = gr.Audio(type="file")
            audio_input.preprocess(x_wav)
            with open("test/test_files/audio_sample.wav") as f:
                audio_input.serialize(f, False)
        audio_input = gr.Audio(type="filepath")
        self.assertIsInstance(audio_input.preprocess(x_wav), str)
        with self.assertRaises(ValueError):
            audio_input = gr.Audio(type="unknown")
            audio_input.preprocess(x_wav)
            audio_input.serialize(x_wav, False)
        audio_input = gr.Audio(type="numpy")
        x_wav = gr.processing_utils.audio_from_file("test/test_files/audio_sample.wav")
        self.assertIsInstance(audio_input.serialize(x_wav, False), dict)

    def test_tokenize(self):
        x_wav = media_data.BASE64_AUDIO
        audio_input = gr.Audio()
        tokens, _, _ = audio_input.tokenize(x_wav)
        self.assertEquals(len(tokens), audio_input.interpretation_segments)
        x_new = audio_input.get_masked_inputs(tokens, [[1] * len(tokens)])[0]
        similarity = SequenceMatcher(a=x_wav["data"], b=x_new).ratio()
        self.assertGreater(similarity, 0.9)

    def test_as_component_as_output(self):
        y_audio = gr.processing_utils.decode_base64_to_file(
            media_data.BASE64_AUDIO["data"]
        )
        audio_output = gr.Audio(type="file")
        self.assertTrue(
            audio_output.postprocess(y_audio.name).startswith(
                "data:audio/wav;base64,UklGRuI/AABXQVZFZm10IBAAA"
            )
        )
        self.assertEqual(
            audio_output.get_template_context(),
            {
                "name": "audio",
                "label": None,
                "source": "upload",
                "css": {},
                "default_value": None,
            },
        )
        self.assertTrue(
            audio_output.deserialize(media_data.BASE64_AUDIO["data"]).endswith(".wav")
        )
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = audio_output.save_flagged(
                tmpdirname, "audio_output", media_data.BASE64_AUDIO, None
            )
            self.assertEqual("audio_output/0.wav", to_save)
            to_save = audio_output.save_flagged(
                tmpdirname, "audio_output", media_data.BASE64_AUDIO, None
            )
            self.assertEqual("audio_output/1.wav", to_save)

    def test_in_interface_as_output(self):
        def generate_noise(duration):
            return 48000, np.random.randint(-256, 256, (duration, 3)).astype(np.int16)

        iface = gr.Interface(generate_noise, "slider", "audio")
        self.assertTrue(iface.process([100])[0][0].startswith("data:audio/wav;base64"))


class TestFile(unittest.TestCase):
    def test_as_component_as_input(self):
        x_file = media_data.BASE64_FILE
        file_input = gr.File()
        output = file_input.preprocess(x_file)
        self.assertIsInstance(output, tempfile._TemporaryFileWrapper)
        self.assertEqual(
            file_input.serialize("test/test_files/sample_file.pdf", True),
            "test/test_files/sample_file.pdf",
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = file_input.save_flagged(tmpdirname, "file_input", [x_file], None)
            self.assertEqual("file_input/0", to_save)
            to_save = file_input.save_flagged(tmpdirname, "file_input", [x_file], None)
            self.assertEqual("file_input/1", to_save)
            restored = file_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, "file_input/1")

        self.assertIsInstance(file_input.generate_sample(), dict)
        file_input = gr.File(label="Upload Your File")
        self.assertEqual(
            file_input.get_template_context(),
            {
                "file_count": "single",
                "name": "file",
                "label": "Upload Your File",
                "css": {},
                "default_value": None,
            },
        )
        self.assertIsNone(file_input.preprocess(None))
        x_file["is_example"] = True
        self.assertIsNotNone(file_input.preprocess(x_file))

    def test_in_interface_as_input(self):
        x_file = media_data.BASE64_FILE

        def get_size_of_file(file_obj):
            return os.path.getsize(file_obj.name)

        iface = gr.Interface(get_size_of_file, "file", "number")
        self.assertEqual(iface.process([[x_file]])[0], [10558])

    def test_as_component_as_output(self):
        def write_file(content):
            with open("test.txt", "w") as f:
                f.write(content)
            return "test.txt"

        iface = gr.Interface(write_file, "text", "file")
        self.assertDictEqual(
            iface.process(["hello world"])[0][0],
            {
                "name": "test.txt",
                "size": 11,
                "data": "data:text/plain;base64,aGVsbG8gd29ybGQ=",
            },
        )
        file_output = gr.File()
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = file_output.save_flagged(
                tmpdirname, "file_output", [media_data.BASE64_FILE], None
            )
            self.assertEqual("file_output/0", to_save)
            to_save = file_output.save_flagged(
                tmpdirname, "file_output", [media_data.BASE64_FILE], None
            )
            self.assertEqual("file_output/1", to_save)


class TestDataframe(unittest.TestCase):
    def test_as_component_as_input(self):
        x_data = [["Tim", 12, False], ["Jan", 24, True]]
        dataframe_input = gr.Dataframe(headers=["Name", "Age", "Member"])
        output = dataframe_input.preprocess(x_data)
        self.assertEqual(output["Age"][1], 24)
        self.assertEqual(output["Member"][0], False)
        self.assertEqual(dataframe_input.preprocess_example(x_data), x_data)
        self.assertEqual(dataframe_input.serialize(x_data, True), x_data)

        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = dataframe_input.save_flagged(
                tmpdirname, "dataframe_input", x_data, None
            )
            self.assertEqual(json.dumps(x_data), to_save)
            restored = dataframe_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(x_data, restored)

        self.assertIsInstance(dataframe_input.generate_sample(), list)
        dataframe_input = gr.Dataframe(
            headers=["Name", "Age", "Member"], label="Dataframe Input"
        )
        self.assertEqual(
            dataframe_input.get_template_context(),
            {
                "headers": ["Name", "Age", "Member"],
                "datatype": "str",
                "row_count": 3,
                "col_count": 3,
                "col_width": None,
                "default_value": [
                    [None, None, None],
                    [None, None, None],
                    [None, None, None],
                ],
                "name": "dataframe",
                "label": "Dataframe Input",
                "max_rows": 20,
                "max_cols": None,
                "overflow_row_behaviour": "paginate",
                "css": {},
            },
        )
        dataframe_input = gr.Dataframe()
        output = dataframe_input.preprocess(x_data)
        self.assertEqual(output[1][1], 24)
        with self.assertRaises(ValueError):
            wrong_type = gr.Dataframe(type="unknown")
            wrong_type.preprocess(x_data)

    def test_in_interface_as_input(self):
        x_data = [[1, 2, 3], [4, 5, 6]]
        iface = gr.Interface(np.max, "numpy", "number")
        self.assertEqual(iface.process([x_data])[0], [6])
        x_data = [["Tim"], ["Jon"], ["Sal"]]

        def get_last(my_list):
            return my_list[-1]

        iface = gr.Interface(get_last, "list", "text")
        self.assertEqual(iface.process([x_data])[0], ["Sal"])

    def test_as_component_as_output(self):
        dataframe_output = gr.Dataframe()
        output = dataframe_output.postprocess(np.zeros((2, 2)))
        self.assertDictEqual(output, {"data": [[0, 0], [0, 0]]})
        output = dataframe_output.postprocess([[1, 3, 5]])
        self.assertDictEqual(output, {"data": [[1, 3, 5]]})
        output = dataframe_output.postprocess(
            pd.DataFrame([[2, True], [3, True], [4, False]], columns=["num", "prime"])
        )
        self.assertDictEqual(
            output,
            {"headers": ["num", "prime"], "data": [[2, True], [3, True], [4, False]]},
        )
        self.assertEqual(
            dataframe_output.get_template_context(),
            {
                "headers": None,
                "max_rows": 20,
                "max_cols": None,
                "overflow_row_behaviour": "paginate",
                "name": "dataframe",
                "label": None,
                "css": {},
                "datatype": "str",
                "row_count": 3,
                "col_count": 3,
                "col_width": None,
                "default_value": [
                    [None, None, None],
                    [None, None, None],
                    [None, None, None],
                ],
                "name": "dataframe",
            },
        )
        with self.assertRaises(ValueError):
            wrong_type = gr.Dataframe(type="unknown")
            wrong_type.postprocess(0)
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = dataframe_output.save_flagged(
                tmpdirname, "dataframe_output", output, None
            )
            self.assertEqual(
                to_save,
                json.dumps(
                    {
                        "headers": ["num", "prime"],
                        "data": [[2, True], [3, True], [4, False]],
                    }
                ),
            )
            self.assertEqual(
                dataframe_output.restore_flagged(tmpdirname, to_save, None),
                {
                    "headers": ["num", "prime"],
                    "data": [[2, True], [3, True], [4, False]],
                },
            )

    def test_in_interface_as_output(self):
        def check_odd(array):
            return array % 2 == 0

        iface = gr.Interface(check_odd, "numpy", "numpy")
        self.assertEqual(
            iface.process([[2, 3, 4]])[0][0], {"data": [[True, False, True]]}
        )


class TestVideo(unittest.TestCase):
    def test_as_component_as_input(self):
        x_video = media_data.BASE64_VIDEO
        video_input = gr.Video()
        output = video_input.preprocess(x_video)
        self.assertIsInstance(output, str)

        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = video_input.save_flagged(tmpdirname, "video_input", x_video, None)
            self.assertEqual("video_input/0.mp4", to_save)
            to_save = video_input.save_flagged(tmpdirname, "video_input", x_video, None)
            self.assertEqual("video_input/1.mp4", to_save)
            restored = video_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(restored, "video_input/1.mp4")

        self.assertIsInstance(video_input.generate_sample(), dict)
        video_input = gr.Video(label="Upload Your Video")
        self.assertEqual(
            video_input.get_template_context(),
            {
                "source": "upload",
                "name": "video",
                "label": "Upload Your Video",
                "css": {},
                "default_value": None,
            },
        )
        self.assertIsNone(video_input.preprocess(None))
        x_video["is_example"] = True
        self.assertIsNotNone(video_input.preprocess(x_video))
        video_input = gr.Video(type="avi")
        # self.assertEqual(video_input.preprocess(x_video)[-3:], "avi")
        with self.assertRaises(NotImplementedError):
            video_input.serialize(x_video, True)

    def test_in_interface_as_input(self):
        x_video = media_data.BASE64_VIDEO
        iface = gr.Interface(lambda x: x, "video", "playable_video")
        self.assertEqual(iface.process([x_video])[0][0]["data"], x_video["data"])

    def test_as_component_as_output(self):
        y_vid = "test/test_files/video_sample.mp4"
        video_output = gr.Video()
        self.assertTrue(
            video_output.postprocess(y_vid)["data"].startswith("data:video/mp4;base64,")
        )
        self.assertTrue(
            video_output.deserialize(media_data.BASE64_VIDEO["data"]).endswith(".mp4")
        )
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = video_output.save_flagged(
                tmpdirname, "video_output", media_data.BASE64_VIDEO, None
            )
            self.assertEqual("video_output/0.mp4", to_save)
            to_save = video_output.save_flagged(
                tmpdirname, "video_output", media_data.BASE64_VIDEO, None
            )
            self.assertEqual("video_output/1.mp4", to_save)


class TestTimeseries(unittest.TestCase):
    def test_as_component_as_input(self):
        timeseries_input = gr.Timeseries(x="time", y=["retail", "food", "other"])
        x_timeseries = {
            "data": [[1] + [2] * len(timeseries_input.y)] * 4,
            "headers": [timeseries_input.x] + timeseries_input.y,
        }
        output = timeseries_input.preprocess(x_timeseries)
        self.assertIsInstance(output, pd.core.frame.DataFrame)

        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = timeseries_input.save_flagged(
                tmpdirname, "video_input", x_timeseries, None
            )
            self.assertEqual(json.dumps(x_timeseries), to_save)
            restored = timeseries_input.restore_flagged(tmpdirname, to_save, None)
            self.assertEqual(x_timeseries, restored)

        self.assertIsInstance(timeseries_input.generate_sample(), dict)
        timeseries_input = gr.Timeseries(
            x="time", y="retail", label="Upload Your Timeseries"
        )
        self.assertEqual(
            timeseries_input.get_template_context(),
            {
                "x": "time",
                "y": ["retail"],
                "name": "timeseries",
                "label": "Upload Your Timeseries",
                "css": {},
                "default_value": None,
            },
        )
        self.assertIsNone(timeseries_input.preprocess(None))
        x_timeseries["range"] = (0, 1)
        self.assertIsNotNone(timeseries_input.preprocess(x_timeseries))

    def test_in_interface_as_output(self):
        timeseries_input = gr.Timeseries(x="time", y=["retail", "food", "other"])
        x_timeseries = {
            "data": [[1] + [2] * len(timeseries_input.y)] * 4,
            "headers": [timeseries_input.x] + timeseries_input.y,
        }
        iface = gr.Interface(lambda x: x, timeseries_input, "dataframe")
        self.assertEqual(
            iface.process([x_timeseries])[0],
            [
                {
                    "headers": ["time", "retail", "food", "other"],
                    "data": [[1, 2, 2, 2], [1, 2, 2, 2], [1, 2, 2, 2], [1, 2, 2, 2]],
                }
            ],
        )

    def test_as_component_as_output(self):
        timeseries_output = gr.Timeseries(label="Disease")

        self.assertEqual(
            timeseries_output.get_template_context(),
            {
                "x": None,
                "y": None,
                "name": "timeseries",
                "label": "Disease",
                "css": {},
                "default_value": None,
            },
        )
        data = {"Name": ["Tom", "nick", "krish", "jack"], "Age": [20, 21, 19, 18]}
        df = pd.DataFrame(data)
        self.assertEqual(
            timeseries_output.postprocess(df),
            {
                "headers": ["Name", "Age"],
                "data": [["Tom", 20], ["nick", 21], ["krish", 19], ["jack", 18]],
            },
        )

        timeseries_output = gr.Timeseries(y="Age", label="Disease")
        output = timeseries_output.postprocess(df)
        self.assertEqual(
            output,
            {
                "headers": ["Name", "Age"],
                "data": [["Tom", 20], ["nick", 21], ["krish", 19], ["jack", 18]],
            },
        )

        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = timeseries_output.save_flagged(
                tmpdirname, "timeseries_output", output, None
            )
            self.assertEqual(
                to_save,
                '{"headers": ["Name", "Age"], "data": [["Tom", 20], ["nick", 21], ["krish", 19], '
                '["jack", 18]]}',
            )
            self.assertEqual(
                timeseries_output.restore_flagged(tmpdirname, to_save, None),
                {
                    "headers": ["Name", "Age"],
                    "data": [["Tom", 20], ["nick", 21], ["krish", 19], ["jack", 18]],
                },
            )


class TestNames(unittest.TestCase):
    # this ensures that `components.get_component_instance()` works correctly when instantiating from components
    def test_no_duplicate_uncased_names(self):
        subclasses = gr.components.Component.__subclasses__()
        unique_subclasses_uncased = set([s.__name__.lower() for s in subclasses])
        self.assertEqual(len(subclasses), len(unique_subclasses_uncased))


class TestLabel(unittest.TestCase):
    def test_as_component(self):
        y = "happy"
        label_output = gr.Label()
        label = label_output.postprocess(y)
        self.assertDictEqual(label, {"label": "happy"})
        self.assertEqual(label_output.deserialize(y), y)
        self.assertEqual(label_output.deserialize(label), y)
        with tempfile.TemporaryDirectory() as tmpdir:
            to_save = label_output.save_flagged(tmpdir, "label_output", label, None)
            self.assertEqual(to_save, y)
            y = {3: 0.7, 1: 0.2, 0: 0.1}
        label_output = gr.Label()
        label = label_output.postprocess(y)
        self.assertDictEqual(
            label,
            {
                "label": 3,
                "confidences": [
                    {"label": 3, "confidence": 0.7},
                    {"label": 1, "confidence": 0.2},
                    {"label": 0, "confidence": 0.1},
                ],
            },
        )
        label_output = gr.Label(num_top_classes=2)
        label = label_output.postprocess(y)
        self.assertDictEqual(
            label,
            {
                "label": 3,
                "confidences": [
                    {"label": 3, "confidence": 0.7},
                    {"label": 1, "confidence": 0.2},
                ],
            },
        )
        with self.assertRaises(ValueError):
            label_output.postprocess([1, 2, 3])

        with tempfile.TemporaryDirectory() as tmpdir:
            to_save = label_output.save_flagged(tmpdir, "label_output", label, None)
            self.assertEqual(to_save, '{"3": 0.7, "1": 0.2}')
            self.assertEqual(
                label_output.restore_flagged(tmpdir, to_save, None),
                {
                    "label": "3",
                    "confidences": [
                        {"label": "3", "confidence": 0.7},
                        {"label": "1", "confidence": 0.2},
                    ],
                },
            )

    def test_in_interface(self):
        x_img = media_data.BASE64_IMAGE

        def rgb_distribution(img):
            rgb_dist = np.mean(img, axis=(0, 1))
            rgb_dist /= np.sum(rgb_dist)
            rgb_dist = np.round(rgb_dist, decimals=2)
            return {
                "red": rgb_dist[0],
                "green": rgb_dist[1],
                "blue": rgb_dist[2],
            }

        iface = gr.Interface(rgb_distribution, "image", "label")
        output = iface.process([x_img])[0][0]
        self.assertDictEqual(
            output,
            {
                "label": "red",
                "confidences": [
                    {"label": "red", "confidence": 0.44},
                    {"label": "green", "confidence": 0.28},
                    {"label": "blue", "confidence": 0.28},
                ],
            },
        )


class TestHighlightedText(unittest.TestCase):
    def test_as_component(self):
        ht_output = gr.HighlightedText(color_map={"pos": "green", "neg": "red"})
        self.assertEqual(
            ht_output.get_template_context(),
            {
                "color_map": {"pos": "green", "neg": "red"},
                "name": "highlightedtext",
                "label": None,
                "show_legend": False,
                "css": {},
                "default_value": "",
            },
        )
        ht = {"pos": "Hello ", "neg": "World"}
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = ht_output.save_flagged(tmpdirname, "ht_output", ht, None)
            self.assertEqual(to_save, '{"pos": "Hello ", "neg": "World"}')
            self.assertEqual(
                ht_output.restore_flagged(tmpdirname, to_save, None),
                {"pos": "Hello ", "neg": "World"},
            )

    def test_in_interface(self):
        def highlight_vowels(sentence):
            phrases, cur_phrase = [], ""
            vowels, mode = "aeiou", None
            for letter in sentence:
                letter_mode = "vowel" if letter in vowels else "non"
                if mode is None:
                    mode = letter_mode
                elif mode != letter_mode:
                    phrases.append((cur_phrase, mode))
                    cur_phrase = ""
                    mode = letter_mode
                cur_phrase += letter
            phrases.append((cur_phrase, mode))
            return phrases

        iface = gr.Interface(highlight_vowels, "text", "highlight")
        self.assertListEqual(
            iface.process(["Helloooo"])[0][0],
            [("H", "non"), ("e", "vowel"), ("ll", "non"), ("oooo", "vowel")],
        )


class TestJSON(unittest.TestCase):
    def test_as_component(self):
        js_output = gr.JSON()
        self.assertTrue(
            js_output.postprocess('{"a":1, "b": 2}'), '"{\\"a\\":1, \\"b\\": 2}"'
        )
        js = {"pos": "Hello ", "neg": "World"}
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = js_output.save_flagged(tmpdirname, "js_output", js, None)
            self.assertEqual(to_save, '{"pos": "Hello ", "neg": "World"}')
            self.assertEqual(
                js_output.restore_flagged(tmpdirname, to_save, None),
                {"pos": "Hello ", "neg": "World"},
            )

    def test_in_interface(self):
        def get_avg_age_per_gender(data):
            return {
                "M": int(data[data["gender"] == "M"].mean()),
                "F": int(data[data["gender"] == "F"].mean()),
                "O": int(data[data["gender"] == "O"].mean()),
            }

        iface = gr.Interface(
            get_avg_age_per_gender,
            gr.inputs.Dataframe(headers=["gender", "age"]),
            "json",
        )
        y_data = [
            ["M", 30],
            ["F", 20],
            ["M", 40],
            ["O", 20],
            ["F", 30],
        ]
        self.assertDictEqual(iface.process([y_data])[0][0], {"M": 35, "F": 25, "O": 20})


class TestHTML(unittest.TestCase):
    def test_in_interface(self):
        def bold_text(text):
            return "<strong>" + text + "</strong>"

        iface = gr.Interface(bold_text, "text", "html")
        self.assertEqual(iface.process(["test"])[0][0], "<strong>test</strong>")


class TestCarousel(unittest.TestCase):
    def test_as_component(self):
        carousel_output = gr.Carousel(
            components=[gr.Textbox(), gr.Image()], label="Disease"
        )

        output = carousel_output.postprocess(
            [
                ["Hello World", "test/test_files/bus.png"],
                ["Bye World", "test/test_files/bus.png"],
            ]
        )
        self.assertEqual(
            output,
            [
                ["Hello World", media_data.BASE64_IMAGE],
                ["Bye World", media_data.BASE64_IMAGE],
            ],
        )

        carousel_output = gr.Carousel(components=gr.Textbox(), label="Disease")
        output = carousel_output.postprocess([["Hello World"], ["Bye World"]])
        self.assertEqual(output, [["Hello World"], ["Bye World"]])
        self.assertEqual(
            carousel_output.get_template_context(),
            {
                "components": [
                    {
                        "name": "textbox",
                        "label": None,
                        "default_value": "",
                        "lines": 1,
                        "css": {},
                        "placeholder": None,
                    }
                ],
                "name": "carousel",
                "label": "Disease",
                "css": {},
            },
        )
        output = carousel_output.postprocess(["Hello World", "Bye World"])
        self.assertEqual(output, [["Hello World"], ["Bye World"]])
        with self.assertRaises(ValueError):
            carousel_output.postprocess("Hello World!")
        with tempfile.TemporaryDirectory() as tmpdirname:
            to_save = carousel_output.save_flagged(
                tmpdirname, "carousel_output", output, None
            )
            self.assertEqual(to_save, '[["Hello World"], ["Bye World"]]')

    def test_in_interface(self):
        carousel_output = gr.Carousel(
            components=[gr.Textbox(), gr.Image()], label="Disease"
        )

        def report(img):
            results = []
            for i, mode in enumerate(["Red", "Green", "Blue"]):
                color_filter = np.array([0, 0, 0])
                color_filter[i] = 1
                results.append([mode, img * color_filter])
            return results

        iface = gr.Interface(report, gr.inputs.Image(type="numpy"), carousel_output)
        result = iface.process([media_data.BASE64_IMAGE])
        self.assertTrue(result[0][0][0][0] == "Red")
        self.assertTrue(
            result[0][0][0][1].startswith("data:image/png;base64,iVBORw0KGgoAAA")
        )
        self.assertTrue(result[0][0][1][0] == "Green")
        self.assertTrue(
            result[0][0][1][1].startswith("data:image/png;base64,iVBORw0KGgoAAA")
        )
        self.assertTrue(result[0][0][2][0] == "Blue")
        self.assertTrue(
            result[0][0][2][1].startswith("data:image/png;base64,iVBORw0KGgoAAA")
        )

    if __name__ == "__main__":
        unittest.main()
