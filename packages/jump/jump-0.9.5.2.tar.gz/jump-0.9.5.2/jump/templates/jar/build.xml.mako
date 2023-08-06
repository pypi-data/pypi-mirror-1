<project name="${dist_name}" default="dist">

    <taskdef name="one-jar"
             classname="com.simontuffs.onejar.ant.OneJarTask"
             classpath="${onejar_jar_filename}"
             onerror="report"/>

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

        <one-jar destfile="${dist_path}.jar">
            <main>
                <fileset dir="${build_class_dir}"/>
            </main>
            <lib>
                % if lib_dir_exists:
                <fileset dir="${lib_dir}"/>
                % endif
                <fileset dir="${build_lib_dir}"/>
                <fileset dir="${jython_dirname}" includes="*.jar"/>
            </lib>
            <binlib>
                % if binlib_dir_exists:
                <fileset dir="${binlib_dir}"/>
                % endif
            </binlib>
            <manifest>
                <attribute name="Main-Class"
                           value="com.simontuffs.onejar.Boot"/>
                <attribute name="One-Jar-Main-Class"
                           value="${main_class}"/>
                <attribute name="Built-By" value="${jump_version}"/>
            </manifest>
            <fileset dir="${build_resc_dir}">
                <include name="**"/>
            </fileset>
        </one-jar>
    </target>

</project>
