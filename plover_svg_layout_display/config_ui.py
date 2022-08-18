from PyQt5.QtWidgets import (
    QDialog, QWidget, QLabel, QDialogButtonBox, QGridLayout,
    QGroupBox, QCheckBox, QVBoxLayout, QLineEdit, QScrollArea,
    QFileDialog, QPushButton, QSpinBox
)
from PyQt5.QtCore import Qt

from plover_svg_layout_display.layout_config import (
    CONFIG_FILE_PARAMS, SYSTEM_NAME_PLACEHOLDER, SYSTEM_PREFIX, 
    LayoutConfig, CONFIG_NAMES, CONFIG_ORDER, CONFIG_TYPES,
    CONFIG_ITEMS
)


FIELD_DATA_WIDTH = 250
PLAIN_TEXT_DATA_HEIGHT = 200


class ConfigUI(QDialog):

    def __init__(
        self, 
        temp_config: LayoutConfig, 
        system_name: str, 
        parent: QWidget = None
    ) -> None:
        super().__init__(parent)
        self.temp_config = temp_config
        self.system_name = system_name
        self.setup_window()

    def select_file(
        self, 
        prompt: str, 
        file_type: str, 
        text_field: QLineEdit
    ) -> None:
        def func() -> None:
            path = QFileDialog.getOpenFileName(
                self, prompt, "", file_type
            )[0]

            if path:
                text_field.setText(path)
        
        return func

    def setup_window(self) -> None:
        self.scroll_widget = QWidget()
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_layout = QVBoxLayout()
        self.fields = dict()

        current_grid_row = 0
        current_grid_layout: QGridLayout = None
        current_groupbox: QGroupBox = None

        for config_name in CONFIG_ORDER:
            if config_name not in CONFIG_NAMES:
                if current_groupbox is not None:
                    current_groupbox.setLayout(current_grid_layout)
                    self.scroll_layout.addWidget(current_groupbox)
                
                current_grid_row = 0
                current_groupbox = QGroupBox()
                current_groupbox.setTitle(config_name)
                current_grid_layout = QGridLayout()
                continue

            if config_name == SYSTEM_NAME_PLACEHOLDER:
                name_label = QLabel()
                name_label.setText(CONFIG_NAMES[config_name])
                name_data = QLabel()
                name_data.setText(self.system_name)

                current_grid_layout.addWidget(
                    name_label, current_grid_row, 0, 1, 1, Qt.AlignRight
                )
                current_grid_layout.addWidget(
                    name_data, current_grid_row, 1, 1, 2, Qt.AlignLeft
                )
                current_grid_row += 1
                continue

            field_label = QLabel()
            field_label.setText(CONFIG_NAMES[config_name])

            field_type = CONFIG_TYPES[config_name]
            field_data = None
            browse_button = None

            if config_name.startswith(SYSTEM_PREFIX):
                if self.system_name not in self.temp_config.system_map:
                    field_value = None
                else:
                    field_value = self.temp_config.system_map[self.system_name].get(
                        config_name, None
                    )
            else:
                field_value = getattr(self.temp_config, config_name)

            if field_value is None and config_name in CONFIG_ITEMS:
                field_value = CONFIG_ITEMS[config_name]

            if field_type == bool:
                field_data = QCheckBox()
                field_data.setChecked(field_value)

            elif field_type == str:
                field_data = QLineEdit()

                if config_name in CONFIG_FILE_PARAMS:
                    prompt, file_type = CONFIG_FILE_PARAMS[config_name]
                    browse_button = QPushButton("Browse", self)
                    browse_button.clicked.connect(self.select_file(
                        prompt, file_type, field_data
                    ))

                field_data.setText(field_value)

            # Note that all integer configs are percentages (for now)
            # So we're hardcoding the limits
            elif field_type == int:
                field_data = QSpinBox()
                field_data.setRange(5, 10000)
                field_data.setSingleStep(5)
                field_data.setSuffix("%")
                field_data.setValue(field_value or 100)

            if field_data is not None:
                field_data.setMinimumWidth(FIELD_DATA_WIDTH)
                current_grid_layout.addWidget(
                    field_label, current_grid_row, 0, 1, 1, Qt.AlignRight
                )

                data_width = 1 + (browse_button is None) * 1

                current_grid_layout.addWidget(
                    field_data, current_grid_row, 1, 1, data_width, Qt.AlignLeft
                )

                if browse_button is not None:
                    current_grid_layout.addWidget(
                        browse_button, current_grid_row, 2, 1, 1, Qt.AlignLeft
                    )

                self.fields[config_name] = field_data
                current_grid_row += 1

        if current_groupbox is not None:
            current_groupbox.setLayout(current_grid_layout)
            self.scroll_layout.addWidget(current_groupbox)

        self.button_box = QDialogButtonBox(
            (
                QDialogButtonBox.Cancel | 
                QDialogButtonBox.Ok
            ),
            parent=self
        )
        self.button_box.rejected.connect(self.reject)
        self.button_box.accepted.connect(self.save_settings)

        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.scroll_area)
        self.layout.addWidget(self.button_box)
        self.setLayout(self.layout)

    def save_settings(self) -> None:
        for config_name in CONFIG_ITEMS.keys():
            field_type = CONFIG_TYPES[config_name]
            field_data = self.fields[config_name]
            field_value = None

            if field_type == bool:
                field_value = field_data.isChecked()
            elif field_type == int:
                field_value = field_data.value()
            elif field_type == str:
                field_value = field_data.text()

            if self.system_name not in self.temp_config.system_map:
                self.temp_config.system_map[self.system_name] = dict()

            if field_value is not None:
                if config_name.startswith(SYSTEM_PREFIX):
                    self.temp_config.system_map[self.system_name][config_name] = field_value
                else:
                    setattr(self.temp_config, config_name, field_value)
        
        self.accept()
