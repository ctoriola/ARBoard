# import the Python Image processing Library
import PIL.Image as Image

def work_on_img():
    # Create an Image object from an Image
    colorImage  = Image.open('data/3d_objects/test.png')

    print(colorImage.size)
    # Resize image
    resized = colorImage.resize((1920, 720))

    # Rotate it by 45 degrees
    transposed  = resized.transpose(Image.ROTATE_90)

    # Display the Image rotated by 45 degrees
    transposed.save('data/3d_objects/texture.png')