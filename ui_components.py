"""
Complete UI components for the dental X-ray analyzer application.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QLabel, QFrame, QGraphicsDropShadowEffect, 
                            QGroupBox, QScrollArea)
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPixmap, QColor
from typing import List, Tuple, Dict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StyleSheet:
    """Central place for application styling."""
    
    CARD_CONTAINER = """
        #cardContainer {
            background-color: white;
            border-radius: 12px;
            border: 1px solid #e0e0e0;
        }
    """
    
    DIAGNOSIS_HEADER = """
        QLabel {
            color: #2c3e50;
            font-size: 18px;
            font-weight: bold;
            padding: 10px;
            background-color: #e3f2fd;
            border-radius: 8px;
            border-left: 4px solid #1976d2;
        }
    """
    
    FINDING_LABEL = """
        QLabel {
            color: #2c3e50;
            font-size: 13px;
            line-height: 1.6;
            padding: 8px;
            background-color: #f8f9fa;
            border-radius: 6px;
            margin: 2px 0px;
        }
        QLabel:hover {
            background-color: #e3f2fd;
        }
    """
    
    CONFIDENCE_HEADER = """
        QLabel {
            color: #0066cc;
            font-size: 14px;
            font-weight: bold;
        }
    """
    
    CONFIDENCE_VALUE = """
        QLabel {
            color: #2c3e50;
            font-size: 24px;
            font-weight: bold;
            margin-top: 5px;
        }
    """

    GROUP_BOX = """
        QGroupBox {
            background-color: #ffffff;
            border-radius: 8px;
            border: 1px solid #e9ecef;
            margin-top: 12px;
            font-weight: bold;
        }
        QGroupBox::title {
            color: #1976d2;
            padding: 5px 10px;
            background-color: transparent;
            font-size: 14px;
        }
    """

    SECTION_HEADER = """
        QLabel {
            color: #2c3e50;
            font-size: 16px;
            font-weight: bold;
            padding: 5px;
            border-bottom: 2px solid #3498db;
            margin-bottom: 10px;
        }
    """

class DiagnosisData:
    """Contains diagnosis-specific data and recommendations."""
    
    FINDINGS_MAP = {
        'nil control': [
            ("✅", "Normal periapical appearance"),
            ("🦷", "Intact lamina dura"),
            ("📏", "Normal periodontal ligament space width"),
            ("🔬", "Healthy bone trabeculation"),
            ("✨", "No pathological findings"),
            ("🌿", "Normal root morphology")
        ],
        'condensing osteitis': [
            ("🔍", "Increased bone density around apex"),
            ("⭕", "Well-defined radioopaque lesion"),
            ("🔥", "Associated with chronic low-grade inflammation"),
            ("🦴", "Localized sclerotic bone reaction"),
            ("😶", "Usually asymptomatic"),
            ("📍", "Commonly seen in mandibular posterior teeth")
        ],
        'diffuse lesion': [
            ("⚠️", "Poorly defined radiolucent area"),
            ("↔️", "Irregular borders"),
            ("📐", "Variable size and shape"),
            ("🦷", "May involve multiple teeth"),
            ("🔨", "Possible bone destruction pattern"),
            ("❓", "Unclear demarcation from healthy bone")
        ],
        'periapical abcess': [
            ("🎯", "Well-defined radiolucent area at apex"),
            ("💔", "Disrupted lamina dura"),
            ("📏", "Widened periodontal ligament space"),
            ("🦴", "Evidence of bone destruction"),
            ("↔️", "May show diffuse borders in acute phase"),
            ("💀", "Associated with non-vital tooth")
        ],
        'periapical granuloma': [
            ("⭕", "Small round/oval radiolucency at apex"),
            ("📏", "Well-defined borders"),
            ("📊", "Size typically < 1cm in diameter"),
            ("💔", "Loss of lamina dura"),
            ("💀", "Associated with non-vital tooth"),
            ("🔍", "Uniform radiolucent appearance")
        ],
        'periapical widening': [
            ("📏", "Increased PDL space width"),
            ("⚡", "Early stage of periapical pathology"),
            ("↔️", "Continuous with periodontal ligament"),
            ("🔥", "May indicate pulpal inflammation"),
            ("📊", "Usually uniform widening"),
            ("🦷", "Intact lamina dura")
        ],
        'pericoronitis': [
            ("🦷", "Partially erupted tooth (usually third molar)"),
            ("🔬", "Soft tissue opacification over crown"),
            ("⚠️", "Possible bone loss around crown"),
            ("📏", "Widened follicular space"),
            ("📍", "May show impaction pattern"),
            ("✅", "Adjacent bone appears normal")
        ],
        'radicular cyst': [
            ("⭕", "Large well-defined radiolucency"),
            ("📏", "Usually > 1cm in diameter"),
            ("🔲", "Corticated border"),
            ("⭕", "Round or oval shape"),
            ("↗️", "May cause root displacement"),
            ("💀", "Associated with non-vital tooth")
        ]
    }

    RECOMMENDATIONS_MAP = {
        'nil control': [
            ("📅", "Regular dental check-ups every 6 months"),
            ("🦷", "Maintain good oral hygiene"),
            ("📸", "Routine radiographic monitoring"),
            ("📚", "Patient education on preventive care")
        ],
        'condensing osteitis': [
            ("⚡", "Pulp vitality testing required"),
            ("🦷", "Evaluate need for endodontic treatment"),
            ("🔍", "Regular monitoring of bone density"),
            ("📊", "Assessment of adjacent teeth"),
            ("📅", "Follow-up in 3 months")
        ],
        'diffuse lesion': [
            ("🔍", "Comprehensive clinical examination needed"),
            ("📸", "Consider CBCT imaging"),
            ("🔬", "Biopsy may be necessary"),
            ("👥", "Specialist consultation recommended"),
            ("📅", "Close monitoring required")
        ],
        'periapical abcess': [
            ("⚡", "Immediate endodontic intervention required"),
            ("💊", "Consider antibiotic prescription"),
            ("🔨", "Possible incision and drainage"),
            ("🦷", "Root canal treatment needed"),
            ("📅", "Short-term follow-up essential")
        ],
        'periapical granuloma': [
            ("🦷", "Root canal treatment indicated"),
            ("🔍", "Regular radiographic monitoring"),
            ("📅", "Follow-up every 3-6 months"),
            ("📊", "Assessment of healing progress"),
            ("👥", "Endodontist consultation if needed")
        ],
        'periapical widening': [
            ("⚡", "Pulp vitality testing essential"),
            ("🔍", "Identify cause of inflammation"),
            ("🦷", "Consider occlusal adjustment"),
            ("📅", "Regular monitoring needed"),
            ("📊", "Track changes over time")
        ],
        'pericoronitis': [
            ("🧼", "Local irrigation and debridement"),
            ("💊", "Antibiotics if systemically involved"),
            ("💉", "Pain management required"),
            ("✂️", "Consider surgical extraction"),
            ("📅", "Short-term follow-up needed")
        ],
        'radicular cyst': [
            ("🦷", "Root canal treatment required"),
            ("✂️", "Surgical enucleation may be needed"),
            ("🔬", "Histopathological examination"),
            ("📸", "Regular radiographic monitoring"),
            ("👥", "Oral surgeon consultation recommended")
        ]
    }

    MANAGEMENT_MAP = {
        'nil control': {
            "Immediate Action": [
                "• Document baseline radiographic appearance",
                "• Record current dental status",
                "• Check oral hygiene status"
            ],
            "Long-term Plan": [
                "• Regular dental check-ups",
                "• Preventive care measures",
                "• Patient education"
            ]
        },
        'condensing osteitis': {
            "Immediate Action": [
                "• Pulp vitality testing",
                "• Pain assessment",
                "• Evaluate need for endodontic treatment"
            ],
            "Long-term Plan": [
                "• Monitor bone density changes",
                "• Regular radiographic assessment",
                "• Address primary inflammation source"
            ]
        },
        'diffuse lesion': {
            "Immediate Action": [
                "• Comprehensive examination",
                "• Additional imaging (CBCT)",
                "• Consider biopsy"
            ],
            "Long-term Plan": [
                "• Regular monitoring",
                "• Specialist referral if needed",
                "• Treatment based on biopsy results"
            ]
        },
        'periapical abcess': {
            "Immediate Action": [
                "• Emergency drainage if needed",
                "• Antibiotic prescription",
                "• Pain management"
            ],
            "Long-term Plan": [
                "• Complete root canal treatment",
                "• Regular follow-up",
                "• Monitor healing progress"
            ]
        },
        'periapical granuloma': {
            "Immediate Action": [
                "• Start root canal treatment",
                "• Pain management if needed",
                "• Assess tooth restorability"
            ],
            "Long-term Plan": [
                "• Complete endodontic therapy",
                "• Regular radiographic assessment",
                "• Monitor healing"
            ]
        },
        'periapical widening': {
            "Immediate Action": [
                "• Pulp vitality testing",
                "• Identify inflammation cause",
                "• Occlusal analysis"
            ],
            "Long-term Plan": [
                "• Monitor PDL width changes",
                "• Regular follow-up",
                "• Address contributing factors"
            ]
        },
        'pericoronitis': {
            "Immediate Action": [
                "• Local debridement",
                "• Prescribe antibiotics if needed",
                "• Pain management"
            ],
            "Long-term Plan": [
                "• Evaluate for extraction",
                "• Improve oral hygiene",
                "• Regular monitoring"
            ]
        },
        'radicular cyst': {
            "Immediate Action": [
                "• Start root canal treatment",
                "• Plan surgical intervention",
                "• Pain management if needed"
            ],
            "Long-term Plan": [
                "• Complete endodontic therapy",
                "• Surgical enucleation",
                "• Regular radiographic monitoring"
            ]
        }
    }

class ImageCard(QWidget):
    """Widget displaying dental X-ray image with analysis results."""
    
    def __init__(self, image_path: str, predictions: List[Tuple[str, float]]):
        super().__init__()
        self.image_path = image_path
        self.predictions = predictions
        self.primary_diagnosis = predictions[0][0].lower() if predictions else "unknown"
        self.setup_ui()

    def setup_ui(self):
        """Setup the card UI layout."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Create container with shadow effect
        container = self._create_container()
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(20, 20, 20, 20)
        container_layout.setSpacing(15)

        # Add components
        self._add_image_section(container_layout)
        self._add_diagnosis_section(container_layout)
        self._add_confidence_section(container_layout)
        self._add_management_section(container_layout)
        self._add_recommendations_section(container_layout)

        main_layout.addWidget(container)

    def _create_container(self) -> QFrame:
        """Create main container with shadow effect."""
        container = QFrame(self)
        container.setObjectName("cardContainer")
        container.setStyleSheet(StyleSheet.CARD_CONTAINER)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(0, 2)
        container.setGraphicsEffect(shadow)
        
        return container

    def _add_image_section(self, layout: QVBoxLayout):
        """Add image display section."""
        image_container = QFrame()
        image_container.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e9ecef;
            }
        """)
        
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(10, 10, 10, 10)
        
        try:
            image_label = QLabel()
            pixmap = QPixmap(self.image_path)
            scaled_pixmap = pixmap.scaled(
                400, 400,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            image_label.setPixmap(scaled_pixmap)
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            image_layout.addWidget(image_label)
            layout.addWidget(image_container)
        except Exception as e:
            logger.error(f"Error loading image {self.image_path}: {str(e)}")
            error_label = QLabel("Error loading image")
            image_layout.addWidget(error_label)

    def _add_diagnosis_section(self, layout: QVBoxLayout):
        """Add diagnosis section with findings."""
        diagnosis_header = QLabel(f"🔍 Diagnosis: {self.primary_diagnosis.title()}")
        diagnosis_header.setStyleSheet(StyleSheet.DIAGNOSIS_HEADER)
        layout.addWidget(diagnosis_header)

        findings_group = self._create_findings_group()
        layout.addWidget(findings_group)

    def _create_findings_group(self) -> QGroupBox:
        """Create findings group with items."""
        group = QGroupBox("📋 Initial Radiographic Assessment")
        group.setStyleSheet(StyleSheet.GROUP_BOX)
        
        layout = QVBoxLayout(group)
        layout.setContentsMargins(15, 20, 15, 15)
        
        findings = self._get_findings_for_diagnosis()
        for icon, text in findings:
            finding_label = QLabel(f"{icon} {text}")
            finding_label.setWordWrap(True)
            finding_label.setStyleSheet(StyleSheet.FINDING_LABEL)
            layout.addWidget(finding_label)
            
        return group

    def _add_confidence_section(self, layout: QVBoxLayout):
        """Add confidence score section."""
        confidence_group = QGroupBox()
        confidence_layout = QVBoxLayout(confidence_group)
        confidence_layout.setContentsMargins(15, 15, 15, 15)
        
        header = QLabel("🎯 Confidence Score")
        header.setStyleSheet(StyleSheet.CONFIDENCE_HEADER)
        
        confidence_score = self.predictions[0][1] * 100 if self.predictions else 0.0
        value = QLabel(f"{confidence_score:.1f}%")
        value.setStyleSheet(StyleSheet.CONFIDENCE_VALUE)
        
        confidence_layout.addWidget(header)
        confidence_layout.addWidget(value)
        layout.addWidget(confidence_group)

    def _add_management_section(self, layout: QVBoxLayout):
        """Add management plan section."""
        management_data = DiagnosisData.MANAGEMENT_MAP.get(self.primary_diagnosis)
        if not management_data:
            return

        management_group = QGroupBox("📋 Management Plan")
        management_group.setStyleSheet(StyleSheet.GROUP_BOX)
        
        management_layout = QVBoxLayout(management_group)
        management_layout.setContentsMargins(15, 20, 15, 15)
        
        # Immediate Action Section
        immediate_header = QLabel("🚨 Immediate Action Required:")
        immediate_header.setStyleSheet(StyleSheet.SECTION_HEADER)
        management_layout.addWidget(immediate_header)
        
        for action in management_data["Immediate Action"]:
            action_label = QLabel(action)
            action_label.setStyleSheet(StyleSheet.FINDING_LABEL)
            management_layout.addWidget(action_label)
        
        # Long-term Plan Section
        longterm_header = QLabel("🎯 Long-term Management Plan:")
        longterm_header.setStyleSheet(StyleSheet.SECTION_HEADER)
        management_layout.addWidget(longterm_header)
        
        for plan in management_data["Long-term Plan"]:
            plan_label = QLabel(plan)
            plan_label.setStyleSheet(StyleSheet.FINDING_LABEL)
            management_layout.addWidget(plan_label)
        
        layout.addWidget(management_group)

    def _add_recommendations_section(self, layout: QVBoxLayout):
        """Add recommendations section."""
        recommendations = self._get_recommendations()
        if recommendations:
            rec_group = QGroupBox("💡 Clinical Recommendations")
            rec_group.setStyleSheet(StyleSheet.GROUP_BOX)
            
            rec_layout = QVBoxLayout(rec_group)
            rec_layout.setContentsMargins(15, 20, 15, 15)
            
            for icon, text in recommendations:
                rec_label = QLabel(f"{icon} {text}")
                rec_label.setStyleSheet(StyleSheet.FINDING_LABEL)
                rec_layout.addWidget(rec_label)
                
            layout.addWidget(rec_group)

    def _get_findings_for_diagnosis(self) -> List[Tuple[str, str]]:
        """Get specific findings based on diagnosis."""
        return DiagnosisData.FINDINGS_MAP.get(self.primary_diagnosis, [])

    def _get_recommendations(self) -> List[Tuple[str, str]]:
        """Get recommendations based on diagnosis."""
        return DiagnosisData.RECOMMENDATIONS_MAP.get(self.primary_diagnosis, [])

    def animate_shadow(self, end_blur: int):
        """Animate container shadow effect."""
        if hasattr(self, 'container_shadow'):
            animation = QPropertyAnimation(self.container_shadow, b"blurRadius")
            animation.setDuration(200)
            animation.setStartValue(self.container_shadow.blurRadius())
            animation.setEndValue(end_blur)
            animation.start()