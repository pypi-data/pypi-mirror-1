import reclee
import unittest


def dummy_clbk(option, opt, value, parser):
    return True

def dummy_type(*args):
    if len(args) > 1:
        return [str(x) for x in args]
    return str(args[0])

class TestOptions(unittest.TestCase):
    def test_old_style(self):
        opt = reclee.make_option(
            "-l", "--log", dest="log"
        )

    def test_new_style(self):
        opt = reclee.make_option(
            "l", "log", metavar="FILE"
        )

    def test_store_with_validation(self):
        opt = reclee.make_option(
            "l", "log", validate=reclee.VALID_FILENAME
        )

    def test_store_with_two_args(self):
        opt = reclee.make_option(
            "l", "log", nargs=2
        )

    def test_store_with_var_args(self):
        opt = reclee.make_option(
            "l", "log", minargs=1, maxargs=4
        )

    def test_store_with_dest(self):
        opt = reclee.make_option(
            "l", "log", dest="logfile"
        )

    def test_store_with_type(self):
        str_opt = reclee.make_option(
            "l", "log", type="string"
        )
        int_opt = reclee.make_option(
            "l", "log", type="int"
        )
        re_opt = reclee.make_option(
            "l", "log", type="re"
        )
        re2_opt = reclee.make_option(
            "l", "log", type=reclee.TYPE_RE
        )
        f_opt = reclee.make_option(
            "l", "log", type=dummy_type
        )

    def test_store_choices(self):
        opt = reclee.make_option(
            "l", "log", choices=["yes","no"]
        )
        a_opt = reclee.make_option(
            "l", "log", validate=reclee.VALID_CHOICES("yes", "no")
        )

    def test_store_default(self):
        opt = reclee.make_option(
            "l", "log", default="test.log"
        )
        
    def test_store_const(self):
        opt = reclee.make_option(
            "l", "log", action="store_const"
        )

    def test_store_const_with_const(self):
        opt = reclee.make_option(
            "l", "log", action="store_const", const="party"
        )

    def test_store_true(self):
        opt = reclee.make_option(
            "l", "log", action="store_true"
        )

    def test_store_false(self):
        opt = reclee.make_option(
            "l", "log", action="store_false"
        )

    def test_append(self):
        opt = reclee.make_option(
            "l", "log", action="append"
        )

    def test_append_with_type(self):
        opt = reclee.make_option(
            "l", "log", action="append", type="
        
    def test_append_with_validate(self):
        opt = reclee.make_option(
            "l", "log", action="append", validate=reclee.VALID_FILENAME
        )

    def test_count(self):
        opt = reclee.make_option(
            "l", "log", action="count"
        )
        
    def test_callback(self):
        opt = reclee.make_option(
            "l", "log", action="callback", callback=clbk
        )
        
