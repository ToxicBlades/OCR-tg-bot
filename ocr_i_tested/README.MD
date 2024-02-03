## Preprocessing how it works(if you want to do it with our loccaly ocr)

1. First step - Normalization <br />
   This process changes the range of pixel intensity values. The purpose of performing normalization is to bring image to range that is normal to sense. OpenCV uses normalize () function for the image normalization.
2. Second step - Skew Correction <br />
   While scanning or taking a picture of any document, it is possible that the scanned or captured image might be slightly skewed sometimes. For the better performance of the OCR, it is good to determine the skewness in image and correct it.
3. Third Step - Image Scaling <br />
   To achieve a better performance of OCR, the image should have more than 300 PPI (pixel per inch). So, if the image size is less than 300 PPI, we need to increase it. We can use the Pillow library for this.
4. Fourth step - Noise Removal <br />
   This step removes the small dots/patches which have high intensity compared to the rest of the image for smoothening of the image. OpenCV’s fast Nl Means Denoising Coloured function can do that easily.
5. Fifth step - Thinning and Skeletonization <br />
   This step is performed for the handwritten text, as different writers use different stroke widths to write. This step makes the width of strokes uniform. This can be done in OpenCV
6. Sixth - Gray Scale image <br />
   This process converts an image from other color spaces to shades of Gray. The colour varies between complete black and complete white. OpenCV’s cvtColor() function perform this task very easily
7. Seventh step - Thresholding or Binarization <br />
   This step converts any colored image into a binary image that contains only two colors black and white. It is done by fixing a threshold (normally half of the pixel range 0-255, i.e., 127). The pixel value having greater than the threshold is converted into a white pixel else into a black pixel. To determine the threshold value according to the image Otsu’s Binarization and Adaptive Binarization can be a better choice. In OpenCV, this can be done as given.
