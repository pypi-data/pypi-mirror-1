<project name="${dist_name}" default="dist">

    <path id="classpath">
        % if lib_dir_exists:
        <fileset dir="${lib_dir}" includes="**/*.jar"/>
        % endif
    </path>

    <target name="dist">
        <javac destdir="${build_class_dir}" srcdir="${base_dir}"
               classpathref="classpath"/>

		<jar destfile="${dist_path}.jar" basedir="${build_class_dir}">
			<manifest>
                <attribute name="Built-By" value="${jump_version}"/>
            </manifest>
		</jar>
    </target>

</project>
