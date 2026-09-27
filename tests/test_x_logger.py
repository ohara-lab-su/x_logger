import multiprocessing
from pathlib import Path

from x_logger import XLogger


def _child_log(logger, text):
    logger.info(text)


def test_independent_instances_do_not_share_handlers(tmp_path: Path):
    a_path = tmp_path / "a.log"
    b_path = tmp_path / "b.log"
    a = XLogger(log_mode="file", log_name=str(a_path))
    b = XLogger(log_mode="file", log_name=str(b_path))
    try:
        a.info("only-a")
        b.info("only-b")
    finally:
        a.close()
        b.close()

    assert "only-a" in a_path.read_text(encoding="utf-8")
    assert "only-b" not in a_path.read_text(encoding="utf-8")
    assert "only-b" in b_path.read_text(encoding="utf-8")
    assert "only-a" not in b_path.read_text(encoding="utf-8")


def test_multiprocess_spawn_single_log(tmp_path: Path):
    path = tmp_path / "spawn.log"
    logger = XLogger(
        log_mode="file",
        log_name=str(path),
        multiprocess=True,
        start_method="spawn",
    )
    ctx = multiprocessing.get_context("spawn")
    try:
        logger.info("parent-message")
        process = ctx.Process(target=_child_log, args=(logger, "child-message"))
        process.start()
        process.join(10)
        assert process.exitcode == 0
    finally:
        logger.close()

    text = path.read_text(encoding="utf-8")
    assert "parent-message" in text
    assert "child-message" in text


def test_multiprocess_fork_single_log(tmp_path: Path):
    if "fork" not in multiprocessing.get_all_start_methods():
        return
    path = tmp_path / "fork.log"
    logger = XLogger(
        log_mode="file",
        log_name=str(path),
        multiprocess=True,
        start_method="fork",
    )
    ctx = multiprocessing.get_context("fork")
    try:
        logger.info("parent-fork")
        process = ctx.Process(target=_child_log, args=(logger, "child-fork"))
        process.start()
        process.join(10)
        assert process.exitcode == 0
    finally:
        logger.close()

    text = path.read_text(encoding="utf-8")
    assert "parent-fork" in text
    assert "child-fork" in text
