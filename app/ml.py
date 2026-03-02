import numpy as np
import onnxruntime as rt


# sess = rt.InferenceSession("diabetes-model.onnx")
# input_name = sess.get_inputs()[0].name
# output_name = sess.get_outputs()[0].name


def predict(pregnancies: int, glucose: int, bmi: float, age: int) -> int:
    # data = np.array([[pregnancies, glucose, bmi, age]], dtype=np.float32)
    # return int(sess.run([output_name], {input_name: data})[0][0] > 0.5)
    return 1
