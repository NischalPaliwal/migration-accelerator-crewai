from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.knowledge.source.pdf_knowledge_source import PDFKnowledgeSource
from .tools import list_tables, get_table_ddl, get_proc_body, get_dependencies, count_rows, sample_rows, list_procedures, write_migration_log, read_migration_log, read_config, read_file, write_file, transpile_oracle_to_bq, create_table, list_views, get_view_ddl, dry_run_bq, count_rows_bq, execute_query

knowledge_pdf = PDFKnowledgeSource(file_paths=["oracle_dbt_migration_knowledge_base.pdf"])

@CrewBase
class OracleBigQueryMigrationCrew():
    """OracleBigQueryMigrationCrew crew"""

    agents: list[BaseAgent]
    tasks: list[Task]
    
    @agent
    def discovery_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['discovery_agent'],
            verbose=True,
            tools=[list_tables, get_table_ddl, get_proc_body, get_dependencies, count_rows, sample_rows, list_procedures, write_migration_log, list_views, get_view_ddl]
        )
    
    @agent
    def classifier_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['classifier_agent'],
            verbose=True,
            tools=[read_migration_log, write_migration_log]
        )
    
    @agent
    def schema_conversion_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['schema_conversion_agent'],
            verbose=True,
            tools=[read_migration_log, write_migration_log, read_file, write_file, read_config, transpile_oracle_to_bq, create_table]
        )
    
    @agent
    def codegen_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['codegen_agent'],
            verbose=True,
            tools=[read_migration_log, write_migration_log, read_file, write_file, read_config, transpile_oracle_to_bq]
        )
    
    @agent
    def validator_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['validator_agent'],
            verbose=True,
            tools=[read_migration_log, write_migration_log, read_file, count_rows_bq, execute_query, dry_run_bq]
        )
    
    @agent
    def supervisor_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['supervisor_agent'],
            verbose=True
        )

    @task
    def discover_oracle_schema_task(self) -> Task:
        return Task(
            config=self.tasks_config['discover_oracle_schema_task'],
            human_input=True
        )
    
    @task
    def classify_complexity_task(self) -> Task:
        return Task(
            config=self.tasks_config['classify_complexity_task'],
            human_input=True
        )
    
    @task
    def convert_schemas_task(self) -> Task:
        return Task(
            config=self.tasks_config['convert_schemas_task'],
            human_input=True
        )
    
    @task
    def convert_low_medium_procs_task(self) -> Task:
        return Task(
            config=self.tasks_config['convert_low_medium_procs_task'],
            human_input=True
        )
    
    @task
    def validate_migrations_task(self) -> Task:
        return Task(
            config=self.tasks_config['validate_migrations_task'],
            human_input=True
        )
    
    @task
    def supervise_migration_task(self) -> Task:
        return Task(
            config=self.tasks_config['supervise_migration_task']
        )

    @crew
    def crew(self) -> Crew:
        """Creates the OracleBigQueryMigrationCrew crew"""

        return Crew(
            agents=[
                self.discovery_agent(),
                self.classifier_agent(),
                self.schema_conversion_agent(),
                self.codegen_agent(),
                self.validator_agent(),
            ],
            tasks=self.tasks,
            process=Process.hierarchical,
            manager_agent=self.supervisor_agent(),
            verbose=True,
            knowledge_sources=[knowledge_pdf],
            checkpoint=True
        )
