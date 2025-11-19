# main.py
"""Weather Application using Flet v0.28.3"""

import flet as ft
from weather_service import WeatherService
from config import Config


class WeatherApp:
    """Main Weather Application class."""

    def __init__(self, page: ft.Page):
        self.page = page
        self.weather_service = WeatherService()

        # New features:
        self.use_celsius = True           # Temperature unit preference
        self.last_weather_data = None     # Stores last data to re-render after unit toggle

        self.setup_page()
        self.build_ui()

    # ---------------------------------------------------------
    # PAGE SETUP
    # ---------------------------------------------------------
    def setup_page(self):
        """Configure page settings."""
        self.page.title = Config.APP_TITLE
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 20
        self.page.window.width = Config.APP_WIDTH
        self.page.window.height = Config.APP_HEIGHT
        self.page.window.resizable = False

        # Center the window on desktop
        self.page.window.center()

    # ---------------------------------------------------------
    # BUILD UI
    # ---------------------------------------------------------
    def build_ui(self):
        """Build the user interface."""
        # Title
        self.title = ft.Text(
            "Weather App",
            size=32,
            weight=ft.FontWeight.BOLD,
            color=ft.Colors.GREEN_700,
        )

        # City input field
        self.city_input = ft.TextField(
            label="Enter city name",
            hint_text="e.g., London, Tokyo, New York",
            border_color=ft.Colors.GREEN_400,
            prefix_icon=ft.Icons.LOCATION_CITY,
            autofocus=True,
            on_submit=self.on_search,
        )

        # Search button
        self.search_button = ft.ElevatedButton(
            "Get Weather",
            icon=ft.Icons.SEARCH,
            on_click=self.on_search,
            style=ft.ButtonStyle(
                color=ft.Colors.LIGHT_GREEN,
                bgcolor=ft.Colors.YELLOW_50,
            ),
        )

        # Temperature unit toggle switch
        self.unit_switch = ft.Switch(
            label="Use °C",
            value=True,
            on_change=self.on_unit_toggle,
        )

        # Weather display container (initially hidden)
        self.weather_container = ft.Container(
            visible=False,
            bgcolor=ft.Colors.YELLOW_50,
            border_radius=10,
            padding=20,
        )

        # Error message
        self.error_message = ft.Text(
            "",
            color=ft.Colors.RED_700,
            visible=False,
        )

        # Loading indicator
        self.loading = ft.ProgressRing(visible=False)

        # Add all components to page
        self.page.add(
            ft.Column(
                [
                    self.title,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.city_input,
                    self.search_button,
                    self.unit_switch,
                    ft.Divider(height=20, color=ft.Colors.TRANSPARENT),
                    self.loading,
                    self.error_message,
                    self.weather_container,
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=10,
            )
        )

    # ---------------------------------------------------------
    # EVENT HANDLERS
    # ---------------------------------------------------------
    def on_search(self, e):
        """Handle search button click or enter key press."""
        self.page.run_task(self.get_weather)

    def on_unit_toggle(self, e):
        """Toggle between Celsius and Fahrenheit."""
        self.use_celsius = self.unit_switch.value
        self.unit_switch.label = "Use °C" if self.use_celsius else "Use °F"

        # If weather already loaded, refresh the view
        if self.last_weather_data:
           self.display_weather(self.last_weather_data)

    async def get_weather(self):
        """Fetch and display weather data."""
        city = self.city_input.value.strip()

        if not city:
            self.show_error("Please enter a city name")
            return

        # Show loading, hide previous results
        self.loading.visible = True
        self.error_message.visible = False
        self.weather_container.visible = False
        self.page.update()

        try:
            weather_data = await self.weather_service.get_weather(city)
            self.display_weather(weather_data)

        except Exception as e:
            self.show_error(str(e))

        finally:
            self.loading.visible = False
            self.page.update()

    # ---------------------------------------------------------
    # DISPLAY WEATHER
    # ---------------------------------------------------------
    def display_weather(self, data: dict):
        """Display weather information with styling and transitions."""

        self.last_weather_data = data

        # Extract data
        city_name = data.get("name", "Unknown")
        country = data.get("sys", {}).get("country", "")
        temp_c = data.get("main", {}).get("temp", 0)
        feels_c = data.get("main", {}).get("feels_like", 0)
        humidity = data.get("main", {}).get("humidity", 0)
        description = data.get("weather", [{}])[0].get("description", "").title()
        condition = data.get("weather", [{}])[0].get("main", "")
        icon_code = data.get("weather", [{}])[0].get("icon", "01d")
        wind_speed = data.get("wind", {}).get("speed", 0)

        # Temperature conversion
        if self.use_celsius:
            temp = temp_c
            feels = feels_c
            unit = "°C"
        else:
            temp = temp_c * 9/5 + 32
            feels = feels_c * 9/5 + 32
            unit = "°F"

        # Weather condition → background colors
        condition_colors = {
            "Clear": ft.Colors.YELLOW_200,
            "Rain": ft.Colors.BLUE_200,
            "Clouds": ft.Colors.GREY_300,
            "Snow": ft.Colors.CYAN_100,
            "Thunderstorm": ft.Colors.DEEP_PURPLE_200,
            "Drizzle": ft.Colors.BLUE_100,
            "Mist": ft.Colors.GREY_200,
        }
        new_color = condition_colors.get(condition, ft.Colors.AMBER_100)

        # Smooth background transition
        self.weather_container.bgcolor = new_color
        self.weather_container.animate = ft.Animation(400, ft.AnimationCurve.EASE)

        # Weather emojis
        emoji_map = {
            "Clear": "☀️",
            "Rain": "🌧",
            "Clouds": "☁️",
            "Snow": "❄️",
            "Thunderstorm": "⚡",
            "Drizzle": "🌦",
            "Mist": "🌫",
        }
        emoji = emoji_map.get(condition, "🌍")

        # Build UI
        self.weather_container.content = ft.Column(
            [
                ft.Text(
                    f"{city_name}, {country}",
                    size=24,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Row(
                    [
                        ft.Image(
                            src=f"https://openweathermap.org/img/wn/{icon_code}@2x.png",
                            width=100,
                            height=100,
                        ),
                        ft.Text(f"{emoji} {description}", size=20, italic=True),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                ft.Text(
                    f"{temp:.1f}{unit}",
                    size=48,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),

                ft.Text(
                    f"Feels like {feels:.1f}{unit}",
                    size=16,
                    color=ft.Colors.GREY_700,
                ),

                ft.Divider(),

                ft.Row(
                    [
                        self.create_info_card(
                            ft.Icons.WATER_DROP, "Humidity", f"{humidity}%"
                        ),
                        self.create_info_card(
                            ft.Icons.AIR, "Wind Speed", f"{wind_speed} m/s"
                        ),
                    ],
                    alignment=ft.MainAxisAlignment.SPACE_EVENLY,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            spacing=10,
        )

        self.weather_container.visible = True
        self.error_message.visible = False
        self.page.update()

    # ---------------------------------------------------------
    # INFO CARD
    # ---------------------------------------------------------
    def create_info_card(self, icon, label, value):
        """Create an info card for weather details."""
        return ft.Container(
            content=ft.Column(
                [
                    ft.Icon(icon, size=30, color=ft.Colors.BLUE_700),
                    ft.Text(label, size=12, color=ft.Colors.GREY_600),
                    ft.Text(
                        value,
                        size=16,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.BLUE_900,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=5,
            ),
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=15,
            width=150,
        )

    # ---------------------------------------------------------
    # ERROR HANDLING
    # ---------------------------------------------------------
    def show_error(self, message: str):
        """Display error message."""
        self.error_message.value = f"❌ {message}"
        self.error_message.visible = True
        self.weather_container.visible = False
        self.page.update()


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------
def main(page: ft.Page):
    WeatherApp(page)


if __name__ == "__main__":
    ft.app(target=main)
