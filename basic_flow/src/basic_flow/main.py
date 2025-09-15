import json
import os
from typing import List, Dict
from pydantic import BaseModel, Field
from crewai import LLM
from crewai.flow.flow import Flow, listen, start
from basic_flow.crews.addl_crew.addl_crew import AddlCrew

class SectionTitle(BaseModel):
    title: str = Field(description="Title of the Section")
    description: str = Field(description="Brief description about the section")

class ReportOutline(BaseModel):
    title: str = Field(description="Title of the Document")
    introduction: str = Field(description="Introduction of the Topic")
    target_audience: str = Field(description="Description of the target audience")
    sections: List[SectionTitle] = Field(description="List of sections in the document")
    conclusion: str = Field(description="Conclusion of the document")

# Flow state starts here
class ReportState(BaseModel):
    topic: str = ""
    audience_level: str = ""
    doc_outline: ReportOutline = None
    section_content: Dict[str,str] = {}

class ReportFlow(Flow[ReportState]):
    """ Flow for creating a comprehensive market research report on trends of any industry """

    @start()
    def get_user_input(self):
        """ Get user input from any specific topic in any area for which market trend is expected"""
        self.state.topic = "Information Technology"
        self.state.audience_level = "Experts of Information Technology Industry, Enterprise Architects and Technology managers"
        return self.state
    
    @listen(get_user_input)
    def create_report_structure(self, state):
        """Create a structured outline for the report using a direct LLM call"""
        print("Creating guide outline...")
        # Initialize the LLM
        llm = LLM(model="openai/gpt-4o-mini", response_format=ReportOutline)

        messages = [
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": f"""
            Create a detailed outline for a comprehensive market trend report on "{state.topic}" for {state.audience_level} level learners.

            The outline should include:
            1. A compelling title for the research report
            2. An introduction to the topic
            3. 4-6 main sections that cover the most important aspects of the topic
            4. A conclusion or summary

            For each section, provide a clear title and a brief description of what it should cover.
            """}
        ]

        # Make the LLM call with JSON response format
        response = llm.call(messages=messages)
        outline_dict = json.loads(response)
        self.state.doc_outline = ReportOutline(**outline_dict)

        # Check for existence of output folder
        os.makedirs("output", exist_ok=True)
        with open("output/doc_outline.json", "w") as f:
            json.dump(outline_dict, f, indent=2)
        return self.state.doc_outline
    

    @listen(create_report_structure)
    def write_full_report(self, outline):
        """Write all sections and compile the market trend report"""
        print("Writing report sections and compiling...")
        completed_sections = []

        # Process one section at a time
        for section in outline.sections:
            print(f"Processing section: {section.title}")
            previous_section_text = ""
            if completed_sections:
                previous_sections_text = "# Previously Written Sections\n\n"
                for title in completed_sections:
                    previous_sections_text += f"## {title}\n\n"
                    previous_sections_text += self.state.section_content.get(title, "") + "\n\n"
            else:
                previous_sections_text = "No previous sections written yet."
            
            # Run the content creation crew for this section
            result = AddlCrew().crew().kickoff(
                inputs={
                    "section_title": section.title,
                    "section_description": section.description,
                    "audience_level": self.state.audience_level,
                    "previous_sections": previous_sections_text,
                    "draft_content": ""
                }
            )

            # Store the content generated
            self.state.section_content[section.title] = result.raw
            completed_sections.append(section.title)
            print(f"Section completed: {section.title}")

        # Finalize the report
        report_content = f"# {outline.title}\n\n"
        report_content += f"## Introduction\n\n{outline.introduction}\n\n"

        # Add sections in order
        for section in outline.sections:
            section_content = self.state.section_content.get(section.title, "")
            report_content += f"\n\n{section_content}\n\n"

        report_content += f"## Conclusion\n\n{outline.conclusion}\n\n"

        with open("output/complete_report.md", "w") as f:
            f.write(report_content)
        print("\nComplete report compiled and saved to output/complete_report.md")
        return "Report creation completed successfully"
    
def kickoff():
    """Run the Report creator flow"""
    ReportFlow().kickoff()
    print("\n=== Flow Complete ===")
    print("Your comprehensive market research report is ready in the output directory.")
    print("Open output/complete_report.md to view it.")


if __name__ == "__main__":
    kickoff()

