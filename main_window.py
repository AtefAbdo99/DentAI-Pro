"""
Main window implementation for the dental X-ray analyzer application.
"""

import sys
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                            QScrollArea, QProgressBar, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import logging
from typing import List, Optional
from pathlib import Path

from model_handler import ModelHandler, PredictionWorker
from ui_components import ImageCard

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DentalXRayAnalyzer(QMainWindow):
    """Main application window for dental X-ray analysis."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DentAI Pro - Advanced Dental X-Ray Analysis System")
        self.setMinimumSize(1200, 800)
        
        # Initialize state
        self.workers: List[PredictionWorker] = []
        self.model_handler: Optional[ModelHandler] = None
        
        try:
            self.init_model()
            self.setup_ui()
        except Exception as e:
            logger.error(f"Failed to initialize application: {str(e)}")
            QMessageBox.critical(self, "Initialization Error", 
                               f"Failed to start application: {str(e)}")
            sys.exit(1)

    def init_model(self):
        """Initialize the model handler."""
        try:
            model_path = os.path.join(os.path.dirname(__file__), 'initial_model.pth')
            self.model_handler = ModelHandler(model_path)
        except Exception as e:
            logger.error(f"Model initialization failed: {str(e)}")
            raise

    def setup_ui(self):
        """Setup the user interface."""
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)

        # Add UI components
        layout.addWidget(self._create_header())
        layout.addWidget(self._create_control_panel())
        
        # Progress bar
        self.progress_bar = self._create_progress_bar()
        layout.addWidget(self.progress_bar)
        
        # Scrollable area for image cards
        layout.addWidget(self._create_scroll_area())

    def _create_header(self) -> QWidget:
        """Create header section with logo and title."""
        header = QWidget()
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 20)

        # Logo
        logo = QLabel("🦷")
        logo.setStyleSheet("font-size: 32px;")
        
        # Title and subtitle
        title_container = QWidget()
        title_layout = QVBoxLayout(title_container)
        
        title = QLabel("DentAI Pro")
        title.setStyleSheet("""
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        subtitle = QLabel("Advanced Dental Radiograph Analysis System")
        subtitle.setStyleSheet("""
            font-size: 18px;
            color: #34495e;
        """)
        
        description = QLabel("Powered by AI for accurate dental pathology detection")
        description.setStyleSheet("""
            font-size: 14px;
            color: #7f8c8d;
            font-style: italic;
        """)
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        title_layout.addWidget(description)
        
        header_layout.addWidget(logo)
        header_layout.addWidget(title_container)
        header_layout.addStretch()
        
        return header

    def _create_control_panel(self) -> QWidget:
        """Create control panel with action buttons."""
        panel = QWidget()
        panel.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        layout = QHBoxLayout(panel)
        layout.setSpacing(15)
        
        # Create buttons
        self.load_btn = self._create_button("📁 Load Radiographs", self.load_images)
        self.clear_btn = self._create_button("🗑️ Clear Analysis", self.clear_images)
        self.export_btn = self._create_button("📊 Export Report", self.export_report)
        
        layout.addWidget(self.load_btn)
        layout.addWidget(self.clear_btn)
        layout.addWidget(self.export_btn)
        
        return panel

    def _create_button(self, text: str, slot: callable) -> QPushButton:
        """Create styled button with connection to slot."""
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2472a4;
            }
        """)
        btn.clicked.connect(slot)
        return btn

    def _create_progress_bar(self) -> QProgressBar:
        """Create progress bar for batch processing."""
        progress_bar = QProgressBar()
        progress_bar.setVisible(False)
        progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                text-align: center;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        return progress_bar

    def _create_scroll_area(self) -> QScrollArea:
        """Create scrollable area for image cards."""
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f5f6fa;
            }
        """)
        
        self.grid_widget = QWidget()
        self.grid_layout = QHBoxLayout(self.grid_widget)
        self.grid_layout.setSpacing(20)
        self.grid_layout.setContentsMargins(20, 20, 20, 20)
        self.grid_layout.addStretch()
        
        scroll.setWidget(self.grid_widget)
        return scroll

    def load_images(self):
        """Load and process dental X-ray images."""
        try:
            file_names, _ = QFileDialog.getOpenFileNames(
                self,
                "Select Dental X-Ray Images",
                "",
                "Images (*.png *.jpg *.jpeg)"
            )
            
            if not file_names:
                return
                
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(file_names))
            self.progress_bar.setValue(0)
            
            for file_name in file_names:
                self._process_image(file_name)
                
        except Exception as e:
            logger.error(f"Error loading images: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load images: {str(e)}")

    def _process_image(self, image_path: str):
        """Process single image with prediction worker."""
        try:
            worker = PredictionWorker(self.model_handler, image_path)
            worker.finished.connect(self._handle_prediction_result)
            worker.error.connect(self._handle_prediction_error)
            self.workers.append(worker)
            worker.start()
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {str(e)}")
            self._handle_prediction_error(str(e))

    def _handle_prediction_result(self, predictions: list, image_path: str):
        """Handle successful prediction result."""
        try:
            card = ImageCard(image_path, predictions)
            self.grid_layout.insertWidget(self.grid_layout.count() - 1, card)
            
            self.progress_bar.setValue(self.progress_bar.value() + 1)
            if self.progress_bar.value() == self.progress_bar.maximum():
                self.progress_bar.setVisible(False)
                self._cleanup_workers()
        except Exception as e:
            logger.error(f"Error handling prediction result: {str(e)}")
            self._handle_prediction_error(str(e))

    def _handle_prediction_error(self, error_message: str):
        """Handle prediction error."""
        QMessageBox.warning(self, "Prediction Error", 
                          f"Error processing image: {error_message}")
        self.progress_bar.setValue(self.progress_bar.value() + 1)

    def _cleanup_workers(self):
        """Clean up finished worker threads."""
        self.workers = [w for w in self.workers if not w.isFinished()]

    def clear_images(self):
        """Clear all image cards."""
        try:
            while self.grid_layout.count() > 1:  # Keep the stretch item
                item = self.grid_layout.takeAt(0)
                if widget := item.widget():
                    widget.deleteLater()
        except Exception as e:
            logger.error(f"Error clearing images: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to clear images: {str(e)}")

    def export_report(self):
        """Export analysis results to PDF."""
        if self.grid_layout.count() <= 1:  # Only stretch item
            QMessageBox.warning(self, "Warning", "No images to export!")
            return
            
        try:
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "Save Report",
                "",
                "PDF Files (*.pdf);;All Files (*)"
            )
            
            if file_name:
                self._generate_pdf_report(file_name)
                QMessageBox.information(self, "Success", 
                                      "Report exported successfully!")
        except Exception as e:
            logger.error(f"Error exporting report: {str(e)}")
            QMessageBox.critical(self, "Error", 
                               f"Failed to export report: {str(e)}")

    def _generate_pdf_report(self, file_path: str):
        """Generate PDF report with analysis results."""
        try:
            from report_generator import ReportGenerator, prepare_case_data
            
            # Collect all cases
            cases = []
            for i in range(self.grid_layout.count() - 1):  # -1 to exclude stretch item
                widget = self.grid_layout.itemAt(i).widget()
                if isinstance(widget, ImageCard):
                    case_data = prepare_case_data(widget)
                    cases.append(case_data)
            
            if not cases:
                raise ValueError("No cases to export")
                
            # Generate report
            generator = ReportGenerator()
            generator.generate_report(file_path, cases)
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {str(e)}")
            raise

    def closeEvent(self, event):
        """Handle application closure."""
        try:
            for worker in self.workers:
                worker.wait()
            super().closeEvent(event)
        except Exception as e:
            logger.error(f"Error during closure: {str(e)}")

def main():
    """Application entry point."""
    try:
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Set app-wide stylesheet
        app.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
        """)
        
        window = DentalXRayAnalyzer()
        window.show()
        
        sys.exit(app.exec())
    except Exception as e:
        logger.critical(f"Application failed to start: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()