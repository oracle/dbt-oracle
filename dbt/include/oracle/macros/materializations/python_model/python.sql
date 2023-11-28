{% macro build_ref_function(model) %}
    {%- set ref_dict = {} -%}
    {%- for _ref in model.refs -%}
        {% set _ref_args = [_ref.get('package'), _ref['name']] if _ref.get('package') else [_ref['name'],] %}
        {%- set resolved = ref(*_ref_args, v=_ref.get('version')) -%}
        {%- if _ref.get('version') -%}
            {% do _ref_args.extend(["v" ~ _ref['version']]) %}
        {%- endif -%}
       {%- do ref_dict.update({_ref_args | join('.'): resolve_model_name(resolved)}) -%}
    {%- endfor -%}

    def ref(*args, **kwargs):
        refs = {{ ref_dict | tojson }}
        key = ".".join(args)
        version = kwargs.get("v") or kwargs.get("version")
        if version:
            key += f".v{version}"
        schema, table = refs[key].split(".")
        # Use oml.sync(schema=schema, table=table)
        dbt_load_df_function = kwargs.get("dbt_load_df_function")
        return dbt_load_df_function(schema=schema.upper(), table=table.upper())

{% endmacro %}

{% macro build_source_function(model) %}

    {%- set source_dict = {} -%}
    {%- for _source in model.sources -%}
        {%- set resolved = source(*_source) -%}
        {%- do source_dict.update({_source | join("."): resolve_model_name(resolved)}) -%}
    {%- endfor -%}

    def source(*args, dbt_load_df_function):
        sources = {{ source_dict | tojson }}
        key = ".".join(args)
        schema, table = sources[key].split(".")
        # Use oml.sync(schema=schema, table=table)
        return dbt_load_df_function(schema=schema.upper(), table=table.upper())

{% endmacro %}

{% macro build_config_dict(model) %}
    {%- set config_dict = {} -%}
    {% set config_dbt_used = zip(model.config.config_keys_used, model.config.config_keys_defaults) | list %}
    {%- for key, default in config_dbt_used -%}
        {# weird type testing with enum, would be much easier to write this logic in Python! #}
        {%- if key == 'language' -%}
          {%- set value = 'python' -%}
        {%- endif -%}
        {%- set value = model.config.get(key, default) -%}
        {%- do config_dict.update({key: value}) -%}
    {%- endfor -%}
    config_dict = {{ config_dict }}
{% endmacro %}

{% macro py_script_postfix(model) %}
def main(action, client_identifier, clientinfo, module):
    import oml
    def set_connection_attributes():
        try:
            connection = oml.core.methods._get_conn()
        except Exception:
            raise
        else:
            session_info = {"action": action,
                            "client_identifier": client_identifier,
                            "clientinfo": clientinfo,
                            "module": module}
            for k, v in session_info.items():
                try:
                    setattr(connection, k, v)
                except AttributeError:
                    pass # ok to be silent, ADB-S Python runtime, complains about print statements

    set_connection_attributes()

    import pandas as pd
    {{ build_ref_function(model ) }}
    {{ build_source_function(model ) }}
    {{ build_config_dict(model) }}

    class config:
        def __init__(self, *args, **kwargs):
            pass

        @staticmethod
        def get(key, default=None):
            return config_dict.get(key, default)

    class this:
        """dbt.this() or dbt.this.identifier"""
        database = "{{ this.database }}"
        schema = "{{ this.schema }}"
        identifier = "{{ this.identifier }}"
        def __repr__(self):
            return "{{ this }}"


    class dbtObj:
        def __init__(self, load_df_function) -> None:
            self.source = lambda *args: source(*args, dbt_load_df_function=load_df_function)
            self.ref = lambda *args: ref(*args, dbt_load_df_function=load_df_function)
            self.config = config
            self.this = this()
            self.is_incremental = {{ is_incremental() }}

    def materialize(df, table, session):
        if isinstance(df, pd.core.frame.DataFrame):
           oml.create(df, table=table)
        elif isinstance(df, oml.core.frame.DataFrame):
           df.materialize(table=table)

    {{ model.raw_code | indent(width=4, first=False, blank=True)}}


{{py_script_comment()}}
{% endmacro %}

{#-- entry point for add instuctions for running compiled_code --#}
{%macro py_script_comment()%}
{%endmacro%}
