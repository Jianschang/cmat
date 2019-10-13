from basic import *
from constants.words import *
from constants.pitch import *
from constants.interval import *
from constants.duration import *

import unittest
from unittest import TestCase

class basic_test(TestCase):

    def test_accidental_initialization(self):
        self.assertIsInstance(Accidental(0),Accidental)
        self.assertIsInstance(Accidental(1),Accidental)

        with self.assertRaises(TypeError):
            Accidental(1.0)
        with self.assertRaises(TypeError):
            Accidental('sharp')

        with self.assertRaises(ValueError):
            Accidental(3)
        with self.assertRaises(ValueError):
            Accidental(-3)

    def test_accidental_caching(self):
        self.assertEqual((double/sharp).alternation,2)
        self.assertEqual((double-flat).alternation,-2)

        with self.assertRaises(ValueError):
            double - double/sharp

    def test_accidental_comparison(self):
        self.assertEqual(sharp,Accidental(1))
        self.assertEqual(natural,Accidental(0))
        # self.assertEqual(natural,None)

    def test_accidental_properties(self):
        self.assertEqual(sharp.symbol,'#')
        self.assertEqual(flat.alternation,-1)
        self.assertEqual(natural.name,'natural')



    def test_pitchclass_initialization(self):
        self.assertIsInstance(PitchClass(0),PitchClass)
        self.assertIsInstance(PitchClass(6,sharp),PitchClass)

        with self.assertRaises(TypeError):
            PitchClass(1.0)
        with self.assertRaises(TypeError):
            PitchClass('C',None)
        with self.assertRaises(TypeError):
            PitchClass(1,-1)

        with self.assertRaises(ValueError):
            PitchClass(8)
        with self.assertRaises(ValueError):
            PitchClass(-2)

    def test_pitchclass_caching(self):
        self.assertIsInstance(E/4,Pitch)
        self.assertEqual((E/flat).accidental,flat)
        self.assertEqual((E/double/flat).accidental,double/flat)

    def test_pitchclass_arithmatic(self):
        self.assertEqual(C-G,P5)
        self.assertEqual(Es-Fb,double/diminished/second)
        self.assertEqual(C-Bx,double/augmented/seventh)
        self.assertEqual(C+major/third,E)
        self.assertEqual(G+diminished/seventh,Fb)

        with self.assertRaises(ValueError):
            Ex + major/second

    def test_pitchclass_comparison(self):
        self.assertNotEqual(E,F)
        self.assertNotEqual(E,Fb)
        self.assertEqual(E,En)

    def test_pitchClass_properties(self):
        self.assertEqual(A.degree,5)
        self.assertEqual(Gs.accidental,sharp)
        self.assertEqual(G.alternation,0)
        self.assertEqual(Ex.name,'Ex')
        self.assertEqual(Bbb.letter,'B')
        self.assertEqual(Bx.chromatic,13)
        self.assertEqual(Cb.PIN,11)
        self.assertEqual(F.enharmonics,[Es,Gbb])



    def test_pitch_initialization(self):
        self.assertIsInstance(Pitch(E,4),Pitch)

        with self.assertRaises(TypeError):
            Pitch(0,4)

        with self.assertRaises(TypeError):
            Pitch(E/flat,4.0)

        with self.assertRaises(ValueError):
            Pitch(F,9)

    def test_pitch_caching(self):
        pass

    def test_pitch_arithmetic(self):
        self.assertEqual(C4 + perfect/fifth, G4)
        self.assertEqual(E4 - major/third, C4)
        self.assertEqual(Bbb4 + triple/augmented/third, Dx5)

        with self.assertRaises(ValueError):
            Bbb4 + quadruple/augmented/third

    def test_pitch_comparison(self):
        self.assertTrue(C4 < G4)
        self.assertTrue(C4 == Cn4)
        self.assertTrue(Eb4 >= Ds4)
        self.assertTrue(A4 == Gx4)


    def test_pitch_properties(self):
        self.assertEqual(As4.name,'A#4')
        self.assertEqual(Es4.degree,2)
        self.assertEqual(G4.octave,4)
        self.assertEqual(C4.number,35)
        self.assertEqual(C4.MIDI,60)
        self.assertEqual(A4.frequency,440)
        self.assertEqual(G4.enharmonics,[Fx4,Abb4])


if __name__ == '__main__':
    unittest.main()

