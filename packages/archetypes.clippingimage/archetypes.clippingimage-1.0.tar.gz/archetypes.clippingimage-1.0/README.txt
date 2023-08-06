Image field for *Archetypes* with different bahaviour at time of scaling.

Archtypes default *ImageField* scales down the image until the whole image fits
into the given scale. It keeps it aspect ratio. I.e. scaling down a 400x300
image to a 200x200 scale result in a 200x150 image.

Same with *ClippingImageField* results in a 200x200 image! It centers the image
horizontal or vertical and tries to keep as much as possible from the original.

written by Jens W. Klein, BlueDynamics Alliance, Klein & Partner KEG, Austria
http://bluedynamics.com 

   