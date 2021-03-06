#!/usr/bin/env python
# encoding: utf-8

import unittest
from mocodo.mcd import *
from mocodo.argument_parser import parsed_arguments

import gettext
gettext.NullTranslations().install()

params = parsed_arguments()

import os


class McdTest(unittest.TestCase):

    def test_entity_recognition(self):
        clauses = [
            u"PROJET: num. projet, nom projet, budget projet",
            u"PROJET ABC: num. projet, nom projet, budget projet",
            u"PROJET CDE:",
        ]
        mcd = Mcd(clauses, params)
        self.assertEqual(mcd.box_count, len(clauses))
        for box in mcd.boxes:
            self.assertEqual(box.kind, "entity")

    def test_association_recognition(self):
        entities = [u"FONCTION:", u"DÉPARTEMENT:", u"EMPLOYÉ:", u"PERSONNE:",
                    u"ÉTUDIANT:", u"DATE:", u"CLIENT:", u"COMMANDE:", u"BANDIT:", u"EMPLOYÉ ABC:"]
        associations = [
            u"ASSUMER, 1N EMPLOYÉ, 1N FONCTION: date début, date fin",
            u"DIRIGER, 11 DÉPARTEMENT, 01 EMPLOYÉ",
            u"ENGENDRER, 0N [Parent] PERSONNE, 1N [Enfant] PERSONNE",
            u"SOUTENIR, XX ÉTUDIANT, XX DATE: note stage",
            u"DF, 0N CLIENT, 11 COMMANDE",
            u"DF2, 0N CLIENT, 11 COMMANDE",
            u"ÊTRE AMI, 0N BANDIT, 0N BANDIT",
            u"ASSURER2, 1N EMPLOYÉ ABC, 1N FONCTION: date début, date fin",
        ]
        clauses = entities + associations
        mcd = Mcd(clauses, params)
        self.assertEqual(mcd.box_count, len(clauses))
        for box in mcd.boxes:
            self.assertEqual(box.kind, "entity" if box.name + ":" in entities else "association")

    def test_rows(self):
        clauses = u"""
            BARATTE: piston, racloir, fusil
            MARTEAU, 0N BARATTE, 11 TINET: ciseaux
            TINET: fendoir, grattoir
            CROCHET: égrenoir, _gorgeoir, bouillie

            DF, 11 BARATTE, 1N ROULEAU
            BALANCE, 0N ROULEAU, 0N TINET: charrue
            BANNETON, 01 CROCHET, 11 FLÉAU, 1N TINET: pulvérisateur
            PORTE, 11 CROCHET, 0N CROCHET

            ROULEAU: tribulum
            HERSE, 1N FLÉAU, 1N FLÉAU

            FLÉAU: battadère, van, mesure
        """.split("\n")
        mcd = Mcd(clauses, params)
        self.assertEqual([element.name for element in mcd.rows[0]], [u"BARATTE", u"MARTEAU", u"TINET", u"CROCHET"])
        self.assertEqual([element.name for element in mcd.rows[1]], [u"DF", u"BALANCE", u"BANNETON", u"PORTE"])
        self.assertEqual([element.name for element in mcd.rows[2]], [u" 0", u"ROULEAU", u"HERSE", u" 1"])
        self.assertEqual([element.name for element in mcd.rows[3]], [u" 2", u"FLÉAU", u" 3", u" 4"])

    def test_layout(self):
        clauses = [
            u"BARATTE: piston, racloir, fusil",
            u"MARTEAU, 0N BARATTE, 11 TINET: ciseaux",
            u"TINET: fendoir, grattoir",
            u"CROCHET: égrenoir, _gorgeoir, bouillie",
            u"",
            u"DF, 11 BARATTE, 1N ROULEAU",
            u"BALANCE, 0N ROULEAU, 0N TINET: charrue",
            u"BANNETON, 01 CROCHET, 11 FLÉAU, 1N TINET: pulvérisateur",
            u"PORTE, 11 CROCHET, 0N CROCHET",
            u"",
            u"ROULEAU: tribulum",
            u"HERSE, 1N FLÉAU, 1N FLÉAU",
            u"",
            u"FLÉAU: battadère, van, mesure",
        ]
        mcd = Mcd(clauses, params)
        self.assertEquals(mcd.get_layout(), range(16))
        self.assertEquals(mcd.get_layout_data(),{
            'col_count': 4,
            'row_count': 4,
            'links': (
                (0, 1), # from BARATTE to MARTEAU
                (0, 4), # from BARATTE to DF
                (1, 2),
                (2, 5),
                (2, 6),
                (3, 6),
                (3, 7),
                (4, 9),
                (5, 9),
                (6, 13),
                (10, 13)
            ),
            'multiplicity': {
                (0, 1): 1,
                (0, 4): 1,
                (1, 0): 1,
                (1, 2): 1,
                (2, 1): 1,
                (2, 5): 1,
                (2, 6): 1,
                (3, 6): 1,
                (3, 7): 2, # 2 links between CROCHET and PORTE
                (4, 0): 1,
                (4, 9): 1,
                (5, 2): 1,
                (5, 9): 1,
                (6, 2): 1,
                (6, 3): 1,
                (6, 13): 1,
                (7, 3): 2, # 2 links between PORTE and CROCHET
                (9, 4): 1,
                (9, 5): 1,
                (10, 13): 2,
                (13, 6): 1,
                (13, 10): 2
            },
            'successors': [
                set([1, 4]), # BARATTE has MARTEAU and DF as successors
                set([0, 2]),
                set([1, 5, 6]),
                set([6, 7]),
                set([0, 9]),
                set([2, 9]),
                set([2, 3, 13]),
                set([3]), # reflexive association PORTE: no multiple edges
                set([]), # phantom
                set([4, 5]),
                set([13]),
                set([]),
                set([]),
                set([6, 10]),
                set([]),
                set([])]
            }
        )
        expected = u"""
            BARATTE: piston, racloir, fusil
            MARTEAU, 0N BARATTE, 11 TINET: ciseaux
            TINET: fendoir, grattoir
            CROCHET: égrenoir, _gorgeoir, bouillie

            DF, 11 BARATTE, 1N ROULEAU
            BALANCE, 0N ROULEAU, 0N TINET: charrue
            BANNETON, 01 CROCHET, 11 FLÉAU, 1N TINET: pulvérisateur
            PORTE, 11 CROCHET, 0N CROCHET

            :
            ROULEAU: tribulum
            HERSE, 1N FLÉAU, 1N FLÉAU
            :

            :
            FLÉAU: battadère, van, mesure
            ::
        """.strip().replace("  ", "")
        self.assertEquals(mcd.get_clauses_from_layout(range(16)), expected)


    def test_input_errors(self):
        clauses = [
            u"PROJET: num. projet, nom projet, budget projet",
            u"ASSUMER, 1N PROJET, 1N INDIVIDU",
        ]
        self.assertRaisesRegexp(RuntimeError, "Mocodo Err.1", Mcd, clauses, params)

    def test_duplicate_errors(self):
        clauses = [
            u"DF, 11 BARATTE, 1N ROULEAU",
            u"BARATTE: piston, racloir, fusil",
            u"TINET: fendoir, grattoir",
            u"BALANCE, 0N ROULEAU, 0N TINET: charrue",
            u"BARATTE: tribulum",
        ]
        self.assertRaisesRegexp(RuntimeError, "Mocodo Err.6", Mcd, clauses, params)
        clauses = [
            u"DF, 11 BARATTE, 1N ROULEAU",
            u"BARATTE: piston, racloir, fusil",
            u"TINET: fendoir, grattoir",
            u"DF, 0N ROULEAU, 0N TINET: charrue",
            u"ROULEAU: tribulum",
        ]
        self.assertRaisesRegexp(RuntimeError, "Mocodo Err.7", Mcd, clauses, params)
        clauses = [
            u"BARATTE, 11 BARATTE, 1N ROULEAU",
            u"BARATTE: piston, racloir, fusil",
            u"TINET: fendoir, grattoir",
            u"BALANCE, 0N ROULEAU, 0N TINET: charrue",
            u"ROULEAU: tribulum",
        ]
        self.assertRaisesRegexp(RuntimeError, "Mocodo Err.8", Mcd, clauses, params)
        clauses = [
            u"BARATTE: piston, racloir, fusil",
            u"BARATTE, 11 BARATTE, 1N ROULEAU",
            u"TINET: fendoir, grattoir",
            u"BALANCE, 0N ROULEAU, 0N TINET: charrue",
            u"ROULEAU: tribulum",
        ]
        self.assertRaisesRegexp(RuntimeError, "Mocodo Err.8", Mcd, clauses, params)

    def test_flip(self):
        clauses = u"""
            BARATTE: piston, racloir, fusil
            MARTEAU, 0N BARATTE, 11 TINET: ciseaux
            TINET: fendoir, grattoir
            CROCHET: égrenoir, _gorgeoir, bouillie

            DF, 11 BARATTE, 1N ROULEAU
            BALANCE, 0N ROULEAU, 0N TINET: charrue
            BANNETON, 01 CROCHET, 11 FLÉAU, 1N TINET: pulvérisateur
            PORTE, 11 CROCHET, 0N CROCHET

            ROULEAU: tribulum
            HERSE, 1N FLÉAU, 1N FLÉAU

            FLÉAU: battadère, van, mesure
        """.split("\n")
        mcd = Mcd(clauses, params)
        expected = u"""
            :
            FLÉAU: battadère, van, mesure
            ::

            :
            ROULEAU: tribulum
            HERSE, 1N FLÉAU, 1N FLÉAU
            :

            DF, 11 BARATTE, 1N ROULEAU
            BALANCE, 0N ROULEAU, 0N TINET: charrue
            BANNETON, 01 CROCHET, 11 FLÉAU, 1N TINET: pulvérisateur
            PORTE, 11 CROCHET, 0N CROCHET

            BARATTE: piston, racloir, fusil
            MARTEAU, 0N BARATTE, 11 TINET: ciseaux
            TINET: fendoir, grattoir
            CROCHET: égrenoir, _gorgeoir, bouillie
        """.strip().replace("  ", "")
        self.assertEquals(mcd.get_clauses_horizontal_mirror(), expected)
        expected = u"""
            CROCHET: égrenoir, _gorgeoir, bouillie
            TINET: fendoir, grattoir
            MARTEAU, 0N BARATTE, 11 TINET: ciseaux
            BARATTE: piston, racloir, fusil

            PORTE, 11 CROCHET, 0N CROCHET
            BANNETON, 01 CROCHET, 11 FLÉAU, 1N TINET: pulvérisateur
            BALANCE, 0N ROULEAU, 0N TINET: charrue
            DF, 11 BARATTE, 1N ROULEAU

            :
            HERSE, 1N FLÉAU, 1N FLÉAU
            ROULEAU: tribulum
            :

            ::
            FLÉAU: battadère, van, mesure
            :
        """.strip().replace("  ", "")
        self.assertEquals(mcd.get_clauses_vertical_mirror(), expected)
        expected = u"""
            BARATTE: piston, racloir, fusil
            DF, 11 BARATTE, 1N ROULEAU
            ::

            MARTEAU, 0N BARATTE, 11 TINET: ciseaux
            BALANCE, 0N ROULEAU, 0N TINET: charrue
            ROULEAU: tribulum
            FLÉAU: battadère, van, mesure

            TINET: fendoir, grattoir
            BANNETON, 01 CROCHET, 11 FLÉAU, 1N TINET: pulvérisateur
            HERSE, 1N FLÉAU, 1N FLÉAU
            :

            CROCHET: égrenoir, _gorgeoir, bouillie
            PORTE, 11 CROCHET, 0N CROCHET
            ::
        """.strip().replace("  ", "")
        self.assertEquals(mcd.get_clauses_diagonal_mirror(), expected)

if __name__ == '__main__':
    unittest.main()
