import os
from click.testing import CliRunner
from create_pdf import cli

def test_basic_create_pdf():
  runner = CliRunner()
  result = runner.invoke(cli, "--front_dir_path test/basic/front --back_dir_path test/basic/back --output_path test/basic/output/game.pdf")
  assert result.exit_code == 0
  assert os.path.exists("test/basic/output/game.pdf")