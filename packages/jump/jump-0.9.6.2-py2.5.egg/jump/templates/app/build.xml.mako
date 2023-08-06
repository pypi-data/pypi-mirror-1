<project name="${dist_name}" default="dist">

    <taskdef name="jarbundler"
             classname="net.sourceforge.jarbundler.JarBundler"
             classpath="${jarbundler_filename}"
             onerror="report"/>

    <path id="classpath">
        % if lib_dir_exists:
        <fileset dir="${lib_dir}" includes="**/*.jar"/>
        % endif
        <fileset dir="${build_lib_dir}" includes="**/*.jar"/>
        % if not java_only:
        <fileset dir="${jython_dirname}" includes="*.jar"/>
        % endif
    </path>

    <target name="dist">
        % if not java_only and jythonlib_not_exist:
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

		<jarbundler dir="${dist_dir}" name="${dist_name}"
		            mainclass="${main_class}"
		            ${'icon="%s"' % icns if icns else ""}
		            ${'shortname="%s"' % short_name if short_name else ""}
		            arguments="${vm_arguments}" vmoptions="${vm_options}"
		            developmentregion="${development_region}"
		            infostring="${info_string}" jvmversion="${jvm_version}"
		            signature="${signature}"
		            startOnMainThread="${start_on_main_thread}">

		    % if lib_dir_exists:
		    <jarfileset dir="${lib_dir}">
		        <include name="**/*.jar"/>
		    </jarfileset>
            % endif
            <jarfileset dir="${build_lib_dir}">
		        <include name="**/*.jar"/>
		    </jarfileset>
		    % if not java_only:
		    <jarfileset dir="${jython_dirname}">
		        <include name="*.jar"/>
		    </jarfileset>
		    % endif
            <jarfileset dir="${base_dir}">
                <include name =""/>
                % for command, pattern in manifest_patterns:
                <${command} name="${pattern}"/>
                % endfor
                <exclude name="build/**"/>
                <exclude name="dist/**"/>
            </jarfileset>
		</jarbundler>
    </target>

</project>
