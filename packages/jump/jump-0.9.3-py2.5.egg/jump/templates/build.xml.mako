<project name="connected_sliders" default="dist">

    <taskdef name="one-jar"
             classname="com.simontuffs.onejar.ant.OneJarTask"
             classpath="${onejar_jar_filename}"
             onerror="report"/>

    <path id="classpath">
        % if lib_dir_exists:
        <fileset dir="${lib_dir}" includes="**/*.jar"/>
        % endif
        <fileset dir="${build_lib_dir}" includes="**/*.jar"/>
    </path>

    <target name="dist">
        <javac destdir="${build_class_dir}" srcdir="${base_dir}"
               classpathref="classpath"/>

        <javac destdir="${build_class_dir}" srcdir="${build_temp_dir}"
               classpathref="classpath"/>

        % if not use_default_jython:
        <unjar src="${lib_dir}/jython.jar" dest="${build_temp_dir}/jython"/>
        <jar destfile="${build_lib_dir}/jython.jar"
             basedir="${build_temp_dir}/jython" excludes="Lib/"/>
        <jar destfile="${build_lib_dir}/jython-lib.jar"
             basedir="${build_temp_dir}/jython/Lib"/>
        % endif

        <one-jar destfile="${dist_dir}/${dist_name}.jar">
            <main>
                <fileset dir="${build_class_dir}"/>
            </main>
            <lib>
                % if lib_dir_exists:
                <fileset dir="${lib_dir}" excludes="jython.jar"/>
                % endif
                <fileset dir="${build_lib_dir}"/>
            </lib>
            <manifest>
                <attribute name="Main-Class"
                           value="com.simontuffs.onejar.Boot"/>
                <attribute name="One-Jar-Main-Class"
                           value="${main_class}"/>
                <attribute name="Built-By" value="Jump"/>
            </manifest>
            <fileset dir="${build_resc_dir}">
                <include name="**"/>
            </fileset>
        </one-jar>
    </target>

</project>
