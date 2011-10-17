

from PIL import Image

def UYVY_RAW2RGB_PIL(data, h, w):
		y=Image.fromstring('L',(w,h),data[1::2])
		u=Image.fromstring('L',(w/2,h),data[0::4]).resize((w,h))
		v=Image.fromstring('L',(w/2,h),data[2::4]).resize((w,h))
		return Image.merge('YCbCr',(y,u,v))
		
w = 1280
h = 720
a = UYVY_RAW2RGB_PIL(open('F0.yuv', 'rb').read() , h, w)
a.save('F0.jpeg', 'JPEG')

a = UYVY_RAW2RGB_PIL(open('F_0_1C6526E1.yuv', 'rb').read() , 288, 384)
a.save('F_0_1C6526E1.jpeg', 'JPEG')
