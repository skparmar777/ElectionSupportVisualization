from PIL import Image
import numpy as np

from wordcloud import WordCloud,ImageColorGenerator

def create_word_cloud(text_file, image_name, save_name):
	text = open(text_file, encoding="utf8").read()	
	image_mask = np.array(Image.open(image_name))
	wc = WordCloud(background_color="white", max_words=2000, mask=image_mask,
                max_font_size=40, random_state=42)
	wc.generate(text)
	image_colors = ImageColorGenerator(image_mask)
	wc.recolor(color_func=image_colors)
	wc.to_file(save_name)

create_word_cloud('speeches.txt', 'trump.jpg', 'test_image.jpg')
