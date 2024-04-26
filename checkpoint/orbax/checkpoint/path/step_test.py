# Copyright 2024 The Orbax Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for Orbax step storage constructs."""

from typing import Iterator
from absl.testing import absltest
from absl.testing import parameterized
from etils import epath
from orbax.checkpoint.path import step as step_lib


class StandardNameFormatTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.directory = epath.Path(
        self.create_tempdir(name='step_dir_test').full_path
    )
    self.step_name_prefix = [
        '',
        '0',
        '1',
        '10',
        '11',
        '00',
        '01',
        '010',
        'a',
        'aa',
        'aaa',
        'tmp',
    ]
    self.step_name_prefix_sep = ['', '.', '_']
    self.step_name_step_prefix = ['', 'a', 'aa', 'aaa', 'tmp']
    self.step_name_step_prefix_sep = ['', '.', '_']
    self.step_name_step = [
        '',
        '0',
        '1',
        '10',
        '11',
        '100',
        '101',
        '111',
        '00',
        '01',
        '000',
        '001',
        '010',
        '011',
        'tmp',
    ]

  def generate_step_names(self) -> Iterator[str]:
    for snf in self.step_name_prefix:
      for snps in self.step_name_prefix_sep:
        for snsp in self.step_name_step_prefix:
          for snsps in self.step_name_step_prefix_sep:
            for sns in self.step_name_step:
              yield f'{snf}{snps}{snsp}{snsps}{sns}'

  @parameterized.named_parameters(
      dict(
          testcase_name='step0',
          step_prefix=None,
          step_format_fixed_length=None,
          step=0,
          expected='0',
      ),
      dict(
          testcase_name='step1',
          step_prefix=None,
          step_format_fixed_length=None,
          step=1,
          expected='1',
      ),
      dict(
          testcase_name='padded0',
          step_prefix=None,
          step_format_fixed_length=2,
          step=0,
          expected='00',
      ),
      dict(
          testcase_name='padded1',
          step_prefix=None,
          step_format_fixed_length=2,
          step=1,
          expected='01',
      ),
      dict(
          testcase_name='padded10',
          step_prefix=None,
          step_format_fixed_length=2,
          step=10,
          expected='10',
      ),
      dict(
          testcase_name='prefix_unpadded0',
          step_prefix='aa',
          step_format_fixed_length=None,
          step=0,
          expected='aa_0',
      ),
      dict(
          testcase_name='prefix_unpadded1',
          step_prefix='aa',
          step_format_fixed_length=None,
          step=1,
          expected='aa_1',
      ),
      dict(
          testcase_name='prefix_padded0',
          step_prefix='aa',
          step_format_fixed_length=2,
          step=0,
          expected='aa_00',
      ),
      dict(
          testcase_name='prefix_padded1',
          step_prefix='aa',
          step_format_fixed_length=2,
          step=1,
          expected='aa_01',
      ),
      dict(
          testcase_name='prefix_padded10',
          step_prefix='aa',
          step_format_fixed_length=2,
          step=10,
          expected='aa_10',
      ),
      dict(
          testcase_name='error.step',
          step_prefix=None,
          step_format_fixed_length=None,
          step=5,
          expected=None,
      ),
      dict(
          testcase_name='error.padded',
          step_prefix=None,
          step_format_fixed_length=2,
          step=111111,
          expected=None,
      ),
      dict(
          testcase_name='error.prefix_unpadded',
          step_prefix='aa',
          step_format_fixed_length=None,
          step=5,
          expected=None,
      ),
      dict(
          testcase_name='error.prefix_padded',
          step_prefix='aa',
          step_format_fixed_length=2,
          step=5,
          expected=None,
      ),
  )
  def test_find_step(
      self,
      step_prefix,
      step_format_fixed_length,
      step,
      expected,
  ):
    for step_dir in self.generate_step_names():
      (self.directory / step_dir).mkdir(parents=True, exist_ok=True)

    name_format = step_lib.standard_name_format(
        step_prefix=step_prefix,
        step_format_fixed_length=step_format_fixed_length,
    )
    if expected is None:
      with self.assertRaises(ValueError):
        _ = name_format.find_step(self.directory, step)
      return

    self.assertEqual(
        self.directory / expected,
        name_format.find_step(self.directory, step).path,
    )

  @parameterized.named_parameters(
      dict(
          testcase_name='step',
          step_prefix=None,
          step_format_fixed_length=None,
          expected=['0', '1', '10', '11', '100', '101', '111'],
      ),
      dict(
          testcase_name='padded',
          step_prefix=None,
          step_format_fixed_length=2,
          expected=['00', '01', '10', '11', '100', '101', '111'],
      ),
      dict(
          testcase_name='prefix_unpadded',
          step_prefix='aa',
          step_format_fixed_length=None,
          expected=[
              'aa_0',
              'aa_1',
              'aa_10',
              'aa_11',
              'aa_100',
              'aa_101',
              'aa_111',
          ],
      ),
      dict(
          testcase_name='prefix_padded',
          step_prefix='aa',
          step_format_fixed_length=2,
          expected=[
              'aa_00',
              'aa_01',
              'aa_10',
              'aa_11',
              'aa_100',
              'aa_101',
              'aa_111',
          ],
      ),
  )
  def test_find_all(
      self,
      step_prefix,
      step_format_fixed_length,
      expected,
  ):
    self.step_name_prefix = ['', '00', '01', '010', 'a', 'aa', 'aaa', 'tmp']

    for step_dir in self.generate_step_names():
      (self.directory / step_dir).mkdir(parents=True, exist_ok=True)

    name_format = step_lib.standard_name_format(
        step_prefix=step_prefix,
        step_format_fixed_length=step_format_fixed_length,
    )
    self.assertSetEqual(
        set(expected),
        set([
            metadata.path.name
            for metadata in name_format.find_all(self.directory)
        ]),
    )


class UtilsTest(parameterized.TestCase):

  def setUp(self):
    super().setUp()
    self.directory = epath.Path(
        self.create_tempdir(name='checkpointing_test').full_path
    )

  @parameterized.parameters(
      (3, 'dir', None, None, None, 'dir/3'),
      (3, 'dir', 'params', None, None, 'dir/3/params'),
      (3, 'dir', 'params', 'checkpoint', None, 'dir/checkpoint_3/params'),
      (3, 'dir', None, None, 2, 'dir/03'),
      (4000, 'dir', 'params', None, 5, 'dir/04000/params'),
      (555, 'dir', 'params', 'foo', 8, 'dir/foo_00000555/params'),
      (1234567890, 'dir', 'params', 'foo', 12, 'dir/foo_001234567890/params'),
  )
  def test_get_save_directory(
      self,
      step,
      directory,
      name,
      step_prefix,
      step_format_fixed_length,
      result,
  ):
    self.assertEqual(
        step_lib.get_save_directory(
            step,
            directory,
            name=name,
            step_prefix=step_prefix,
            step_format_fixed_length=step_format_fixed_length,
        ),
        epath.Path(result),
    )

  def test_get_save_directory_tmp_dir_override(self):
    self.assertEqual(
        step_lib.get_save_directory(
            42,
            'path/to/my/dir',
            name='params',
            step_prefix='foobar_',
            override_directory='a/different/dir/path',
        ),
        epath.Path('a/different/dir/path/params'),
    )

  @parameterized.parameters((None,), ('checkpoint_',), ('foobar_',))
  def test_is_tmp_checkpoint(self, step_prefix):
    step_dir = step_lib.get_save_directory(
        5, self.directory, step_prefix=step_prefix
    )
    step_dir.mkdir(parents=True)
    self.assertFalse(step_lib.is_tmp_checkpoint(step_dir))
    tmp_step_dir = step_lib.create_tmp_directory(step_dir)
    self.assertTrue(step_lib.is_tmp_checkpoint(tmp_step_dir))

    item_dir = step_lib.get_save_directory(
        10, self.directory, name='params', step_prefix=step_prefix
    )
    item_dir.mkdir(parents=True)
    self.assertFalse(step_lib.is_tmp_checkpoint(item_dir))
    tmp_item_dir = step_lib.create_tmp_directory(item_dir)
    self.assertTrue(step_lib.is_tmp_checkpoint(tmp_item_dir))

  @parameterized.parameters(
      ('0', 0),
      ('0000', 0),
      ('1000', 1000),
      ('checkpoint_0', 0),
      ('checkpoint_0000', 0),
      ('checkpoint_003400', 3400),
      ('foobar_1000', 1000),
      ('0.orbax-checkpoint-tmp-1010101', 0),
      ('0000.orbax-checkpoint-tmp-12323232', 0),
      ('foobar_1.orbax-checkpoint-tmp-12424424', 1),
      ('foobar_000505.orbax-checkpoint-tmp-13124', 505),
      ('checkpoint_16.orbax-checkpoint-tmp-123214324', 16),
  )
  def test_step_from_checkpoint_name(self, name, step):
    self.assertEqual(step_lib.step_from_checkpoint_name(name), step)

  @parameterized.parameters(
      ('abc',),
      ('checkpoint_',),
      ('checkpoint_1010_',),
      ('_191',),
      ('.orbax-checkpoint-tmp-191913',),
      ('0.orbax-checkpoint-tmp-',),
      ('checkpoint_.orbax-checkpoint-tmp-191913',),
  )
  def test_step_from_checkpoint_name_invalid(self, name):
    with self.assertRaises(ValueError):
      step_lib.step_from_checkpoint_name(name)

  def test_checkpoint_steps_paths_nonexistent_directory_fails(self):
    with self.assertRaisesRegex(ValueError, 'does not exist'):
      step_lib.checkpoint_steps_paths('/non/existent/dir')

  def test_checkpoint_steps_paths_returns_finalized_paths(self):
    digit_only_path = epath.Path(self.directory / '2')
    digit_only_path.mkdir()
    prefix_path = epath.Path(self.directory / 'checkpoint_01')
    prefix_path.mkdir()
    epath.Path(self.directory / 'checkpoint').mkdir()
    epath.Path(self.directory / '1000.orbax-checkpoint-tmp-1010101').mkdir()

    self.assertCountEqual(
        step_lib.checkpoint_steps_paths(self.directory),
        [digit_only_path, prefix_path],
    )

  def test_checkpoint_steps_returns_steps_of_finalized_paths(self):
    epath.Path(self.directory / '2').mkdir()
    epath.Path(self.directory / 'checkpoint_01').mkdir()
    epath.Path(self.directory / 'checkpoint').mkdir()
    epath.Path(self.directory / '1000.orbax-checkpoint-tmp-1010101').mkdir()

    self.assertSameElements(
        [1, 2],
        step_lib.checkpoint_steps(self.directory),
    )


if __name__ == '__main__':
  absltest.main()
