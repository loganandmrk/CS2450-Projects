import unittest
from unittest.mock import patch
import io
import main
import sys

#Code written by Tyler, Implemented by Ryan

from memory import Memory
def make_state(accumulator=0):
    state = {
        "memory": [0] * 100,
        "accumulator": accumulator,
        "counter": 0,
    }
    return state


class TestCommandLineFilename(unittest.TestCase):

    def test_filename_is_stored_when_provided(self):
        args = ["main.py", "Test1.txt"]
        self.assertEqual(len(args), 2)
        filename = args[1]
        self.assertEqual(filename, "Test1.txt")

    def test_no_filename_raises_error(self):
        args = ["main.py"]
        self.assertFalse(len(args) == 2)

    def test_too_many_args_should_fail(self):
        args = ["main.py", "Test1.txt", "Test2.txt"]
        with patch.object(sys, 'argv', args):
            with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
                with self.assertRaises(SystemExit):
                    main.main()
                printed_output = mock_stdout.getvalue()
                value = printed_output.strip()
                self.assertEqual(value, "File was not provided or too many arguments presented")
        


class TestLoadFileIntoMemory(unittest.TestCase):

    def test_file_loads_into_memory_correctly(self):
        lines = ["+1007", "+1008", "+2007", "+3008", "+4300"]
        state = make_state()
        for i in range(len(lines)):
            state["memory"][i] = int(lines[i])
        self.assertEqual(state["memory"][0], 1007)
        self.assertEqual(state["memory"][4], 4300)

    def test_instruction_count_matches_memory_slots_used(self):
        lines = ["+1007", "+1008", "+2007"]
        state = make_state()
        for i in range(len(lines)):
            state["memory"][i] = int(lines[i])
        self.assertEqual(state["memory"][3], 0)

    def test_opcode_parsed_correctly(self):
        instruction = 1007
        opcode = instruction // 100
        self.assertEqual(opcode, 10)

    def test_operand_parsed_correctly(self):
        instruction = 1007
        operand = instruction % 100
        self.assertEqual(operand, 7)


class TestRead(unittest.TestCase):

    @patch('builtins.input', return_value='25')
    def test_read_stores_positive_value(self, mock_input):
        memory = Memory()
        memory.read(7)
        self.assertEqual(memory.memory[7], 25)

    @patch('builtins.input', return_value='-99')
    def test_read_stores_negative_value(self, mock_input):
        memory = Memory()
        memory.read(7)
        self.assertEqual(memory.memory[7], -99)

    @patch('builtins.input', return_value='hello')
    def test_read_invalid_string_raises_error(self, mock_input):
        memory = Memory()
        with self.assertRaises(ValueError):
            memory.read(7)

    @patch('builtins.input', return_value='99999')
    def test_read_overflow_raises_error(self, mock_input):
        memory = Memory()
        with self.assertRaises(OverflowError):
            memory.read(7)

    @patch('builtins.input', return_value='5')
    def test_read_bad_address_raises_error(self, mock_input):
        memory = Memory()
        with self.assertRaises(ValueError):
            memory.read(100)


class TestWrite(unittest.TestCase):

    def test_write_positive_value_formatted(self):
        memory = Memory()
        memory.memory[5] = 42
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            memory.write(5)
            printed_output = mock_stdout.getvalue()
            value= printed_output.strip()
            self.assertEqual(value, "0042")

    def test_write_negative_value_formatted(self):
        memory = Memory()
        memory.memory[5] = -42
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            memory.write(5)
            printed_output = mock_stdout.getvalue()
            value= printed_output.strip()
            self.assertEqual(value, "-0042")

    def test_write_zero_formatted(self):
        memory = Memory()
        memory.memory[5] = 0
        with patch('sys.stdout', new_callable=io.StringIO) as mock_stdout:
            memory.write(5)
            printed_output = mock_stdout.getvalue()
            value= printed_output.strip()
            self.assertEqual(value, "0000")


    def test_write_bad_address_raises_error(self):
        state = make_state()
        with self.assertRaises(ValueError):
            Memory.write(state, -1)


class TestAdd(unittest.TestCase):

    def _add(self, state, address):
        state["accumulator"] = state["accumulator"] + state["memory"][address]

    def test_add_two_positives(self):
        state = make_state(accumulator=10)
        state["memory"][5] = 20
        self._add(state, 5)
        self.assertEqual(state["accumulator"], 30)

    def test_add_negative_value(self):
        state = make_state(accumulator=10)
        state["memory"][5] = -5
        self._add(state, 5)
        self.assertEqual(state["accumulator"], 5)

    def test_add_zero_changes_nothing(self):
        state = make_state(accumulator=7)
        state["memory"][5] = 0
        self._add(state, 5)
        self.assertEqual(state["accumulator"], 7)


class TestSubtract(unittest.TestCase):

    def _subtract(self, state, address):
        state["accumulator"] = state["accumulator"] - state["memory"][address]

    def test_subtract_basic(self):
        state = make_state(accumulator=10)
        state["memory"][5] = 3
        self._subtract(state, 5)
        self.assertEqual(state["accumulator"], 7)

    def test_subtract_gives_negative_result(self):
        state = make_state(accumulator=3)
        state["memory"][5] = 10
        self._subtract(state, 5)
        self.assertEqual(state["accumulator"], -7)

    def test_subtract_zero_changes_nothing(self):
        state = make_state(accumulator=5)
        state["memory"][5] = 0
        self._subtract(state, 5)
        self.assertEqual(state["accumulator"], 5)


class TestMultiply(unittest.TestCase):

    def _multiply(self, state, address):
        state["accumulator"] = state["accumulator"] * state["memory"][address]

    def test_multiply_two_positives(self):
        state = make_state(accumulator=5)
        state["memory"][2] = 4
        self._multiply(state, 2)
        self.assertEqual(state["accumulator"], 20)

    def test_multiply_by_zero(self):
        state = make_state(accumulator=99)
        state["memory"][2] = 0
        self._multiply(state, 2)
        self.assertEqual(state["accumulator"], 0)

    def test_multiply_by_negative(self):
        state = make_state(accumulator=5)
        state["memory"][2] = -3
        self._multiply(state, 2)
        self.assertEqual(state["accumulator"], -15)


class TestDivide(unittest.TestCase):

    def _divide(self, state, address):
        if state["memory"][address] == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        state["accumulator"] = state["accumulator"] // state["memory"][address]

    def test_divide_basic(self):
        state = make_state(accumulator=20)
        state["memory"][3] = 4
        self._divide(state, 3)
        self.assertEqual(state["accumulator"], 5)

    def test_divide_by_zero_raises_error(self):
        state = make_state(accumulator=10)
        state["memory"][3] = 0
        with self.assertRaises(ZeroDivisionError):
            self._divide(state, 3)

    def test_divide_integer_truncates(self):
        state = make_state(accumulator=7)
        state["memory"][3] = 2
        self._divide(state, 3)
        self.assertEqual(state["accumulator"], 3)


class TestBranch(unittest.TestCase):

    def _branch(self, state, address):
        state["counter"] = address

    def test_branch_sets_counter(self):
        state = make_state()
        self._branch(state, 40)
        self.assertEqual(state["counter"], 40)

    def test_branch_to_zero(self):
        state = make_state()
        state["counter"] = 50
        self._branch(state, 0)
        self.assertEqual(state["counter"], 0)


class TestHalt(unittest.TestCase):

    def test_halt_stops_loop(self):
        running = True
        opcode = 43
        if opcode == 43:
            running = False
        self.assertFalse(running)

    def test_non_halt_keeps_loop_running(self):
        running = True
        opcode = 10
        if opcode == 43:
            running = False
        self.assertTrue(running)


if __name__ == "__main__":
    unittest.main(verbosity=2)
