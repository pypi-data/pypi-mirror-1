import unittest
import os.path

class TestSimple(unittest.TestCase):

    def setUp(self):
        global Image, Color, CompositeOp, VirtualPixelMethod, ChannelType
        from magickpy import Image, Color, CompositeOp, VirtualPixelMethod, ChannelType
        self.samplepath = os.path.join(os.path.dirname(__file__), 'sample.jpg')
        self.samplepath2 = os.path.join(os.path.dirname(__file__), 'star.png')
        self.outputpath = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'build', 'sample.jpg')

    def testInstantiated(self):
        from magickpy import lib
        self.assertTrue(lib.IsMagickInstantiated())

    def testCreate(self):
        self.assertTrue(Image())

    def testRead(self):
        res = Image.read(self.samplepath)
        self.assertTrue(res)
        return res

    def testRead2(self):
        res = Image.read(self.samplepath2)
        self.assertTrue(res)
        return res

    def testWrite(self):
        im = Image.read(self.samplepath)
        self.assertTrue(im.write(self.outputpath))

    def testSize(self):
        im = self.testRead()
        self.assertEquals(615, im.width)
        self.assertEquals(410, im.height)

    def testCrop(self):
        im = self.testRead()
        im2 = im.makeCrop(100, 101, 0, 0)
        self.assertEquals(100, im2.width)
        self.assertEquals(101, im2.height)

    def testBackgroundColor(self):
        im = self.testRead()
        im.setBackgroundColor(Color(0.5, 0.5, 0.5))

    def testMatte(self):
        im = self.testRead()
        im.setMatte(True)
        im.setMatte(False)

    def testComposite(self):
        im = self.testRead()
        im2 = self.testRead2()
        im.applyComposite(CompositeOp.CopyOpacity, im2, 10, 10)

    def testVirtualPixel(self):
        im = self.testRead()
        im.setVirtualPixelMethod(VirtualPixelMethod.Background)

    def testBlur(self):
        im = self.testRead2()
        im2 = im.makeBlur(0, 2)

    def testAdaptiveBlur(self):
        im = self.testRead2()
        im2 = im.makeAdaptiveBlur(0, 2)

    def testGaussianBlur(self):
        im = self.testRead2()
        im2 = im.makeGaussianBlur(0, 2)

    def testMotionBlur(self):
        im = self.testRead2()
        im2 = im.makeMotionBlur(0, 2, 120)

    def testShade(self):
        im = self.testRead()
        im2 = im.makeShade(True, 120, 21.78)

    def testNormalize(self):
        im = self.testRead()
        im.applyNormalize()

    def testContrastStretch(self):
        im = self.testRead()
        im.applyContrastStretch("0%")

    def testColorize(self):
        im = self.testRead()
        im2 = im.makeColorize(Color(0.5, 0.5, 0.5), 50)

    def testSigmoidalContrast(self):
        im = self.testRead()
        im.applySigmoidalContrast(False, "5x50%")

    def testSeparateChannel(self):
        im = self.testRead()
        im.applySeparateChannel(ChannelType.Matte)

    def testCopy(self):
        im = self.testRead()
        im2 = im.copy()

    def testNegateImage(self):
        im = self.testRead()
        im.applyNegate(False)
