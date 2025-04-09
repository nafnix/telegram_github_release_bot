from typing import Sequence, overload

from telegram import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
)


async def edit_message(
    query: CallbackQuery,
    text: str,
    keyboard: InlineKeyboardMarkup | None = None,
) -> Message | bool:
    # See https://core.telegram.org/bots/api#callbackquery
    await query.answer()

    return await query.edit_message_text(text=text, reply_markup=keyboard)


def build_cb_query_data(
    *args: tuple[str, str | int] | str,
    page: int | None = None,
    **kwargs,
):
    """构建查询参数"""

    params: list[tuple[str, str | int]] = []
    for arg in args:
        if isinstance(arg, str):
            params.append((arg, ""))
        else:
            params.append(arg)
    params.extend(kwargs.items())
    if page is not None:
        params.append(("page", page))
    queries = [f"{key}={value}" for key, value in params]
    return "&".join(queries)


_InlineButtons = InlineKeyboardButton | Sequence[InlineKeyboardButton]


@overload
def build_menu(
    buttons: InlineKeyboardButton,
    cols: int | None = None,
    header_buttons: _InlineButtons | None = None,
    page_buttons: _InlineButtons | None = None,
    footer_buttons: _InlineButtons | None = None,
): ...


@overload
def build_menu(
    buttons: Sequence[InlineKeyboardButton],
    cols: int,
    header_buttons: _InlineButtons | None = None,
    page_buttons: _InlineButtons | None = None,
    footer_buttons: _InlineButtons | None = None,
): ...


def build_menu(
    buttons: _InlineButtons,
    cols: int | None = None,
    header_buttons: _InlineButtons | None = None,
    page_buttons: _InlineButtons | None = None,
    footer_buttons: _InlineButtons | None = None,
) -> InlineKeyboardMarkup:
    """构建菜单

    构建一个内联键盘

    :param buttons: 内联按钮列表
    :param cols: 每行多少列
    :param page_buttons: 页按钮, defaults to None
    :param header_buttons: 第一行的按钮, defaults to None
    :param footer_buttons: 最后一行的按钮, defaults to None
    :return: 内联键盘
    """

    menu = []

    if header_buttons:
        menu.append(
            header_buttons
            if isinstance(header_buttons, list)
            else [header_buttons],
        )

    if isinstance(buttons, InlineKeyboardButton):
        menu.append([buttons])
    else:
        if cols is None:
            msg = "cols 是必要参数, 请传入有效的数值"
            raise ValueError(msg)
        menu.extend(
            buttons[i : i + cols] for i in range(0, len(buttons), cols)
        )

    if page_buttons:
        menu.append(page_buttons)

    if footer_buttons:
        menu.append(
            footer_buttons
            if isinstance(footer_buttons, list)
            else [footer_buttons]
        )

    return InlineKeyboardMarkup(menu)


def build_keyboard(
    *buttons: str,
    cols: int | None = None,
) -> ReplyKeyboardMarkup:
    """构建键盘"""

    keyboard = []

    if cols is None:
        keyboard.extend([buttons])
    else:
        keyboard.extend(
            buttons[i : i + cols] for i in range(0, len(buttons), cols)
        )
    return ReplyKeyboardMarkup(keyboard)


UndefinedCallbackData = str(id(object))
