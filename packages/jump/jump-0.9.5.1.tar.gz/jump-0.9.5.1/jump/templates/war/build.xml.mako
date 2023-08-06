<project name="${dist_name}" default="dist">

    <path id="classpath">
        % if lib_dir_exists:
        <fileset dir="${lib_dir}" includes="**/*.jar"/>
        % endif
        <fileset dir="${build_lib_dir}" includes="**/*.jar"/>
        <fileset dir="${jython_dirname}" includes="*.jar"/>
    </path>

    <target name="dist">
        % if jythonlib_not_exist:
        <jar destfile="${jythonlib_jar_filename}"
             basedir="${jythonlib_dirname}"
             excludes="site-packages/" includes="**/*.py"/>
        % endif

        <javac destdir="${build_class_dir}" srcdir="${base_dir}"
               classpathref="classpath"/>

        <javac destdir="${build_class_dir}" srcdir="${build_temp_dir}"
               classpathref="classpath"/>

        <jar destfile="${build_lib_dir}/main.jar" basedir="${build_class_dir}">
        	<manifest>
                <attribute name="Built-By" value="${jump_version}"/>
            </manifest>
        </jar>

        <war destfile="${dist_path}.war" webxml="${web_xml_filename}">
            % if lib_dir_exists:
		    <lib dir="${lib_dir}">
		        <include name="**/*.jar"/>
		    </lib>
            % endif
            <lib dir="${build_lib_dir}">
		        <include name="**/*.jar"/>
		    </lib>
		    <lib dir="${jython_dirname}">
		        <include name="*.jar"/>
		    </lib>
		    % if google_app_engine:
            <webinf dir="${build_temp_dir}">
                <include name="${appengine_xml_filename}"/>
            </webinf>
            % endif
            <manifest>
                <attribute name="Built-By" value="${jump_version}"/>
            </manifest>
        </war>
    </target>

</project>
