"""RGB カラーを表すバリューオブジェクトモジュール。"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Color:
    """RGB カラーを表す不変バリューオブジェクト。

    Attributes:
        r: 赤成分 (0〜255)。
        g: 緑成分 (0〜255)。
        b: 青成分 (0〜255)。
    """

    r: int
    g: int
    b: int

    # 各チャンネルの有効範囲
    _CHANNEL_MIN: int = 0
    _CHANNEL_MAX: int = 255

    def __post_init__(self) -> None:
        """全チャンネルの値が 0〜255 の範囲内であることを検証する。

        Raises:
            ValueError: いずれかのチャンネル値が範囲外の場合。
        """
        for channel_name, value in (("r", self.r), ("g", self.g), ("b", self.b)):
            if not (self._CHANNEL_MIN <= value <= self._CHANNEL_MAX):
                raise ValueError(
                    f"チャンネル '{channel_name}' の値 {value} は "
                    f"{self._CHANNEL_MIN}〜{self._CHANNEL_MAX} の範囲外です。"
                )

    def to_tuple(self) -> tuple[int, int, int]:
        """(r, g, b) のタプルを返す。

        Returns:
            RGB 値を格納した 3 要素タプル。
        """
        return (self.r, self.g, self.b)
