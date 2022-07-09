from fastai.vision.all import *
learn = load_learner('stage1.pkl')

categories1 = 'discarded clothing', 'food waste', 'plastic bags', 'recyc_no_scrap', 'scrap metal piece', 'wood scraps'

def classify_stage1(img):
    pred, idx, probs = learn.predict(img)
    return dict(zip(categories1, map(float,probs)))

# print(classify_stage1('stage1ex1_t.jpeg'))