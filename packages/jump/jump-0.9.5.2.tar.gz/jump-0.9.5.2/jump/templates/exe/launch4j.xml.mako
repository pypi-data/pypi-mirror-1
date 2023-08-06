<launch4jConfig>
    <headerType>${'gui' if gui else 'console'}</headerType>
    <outfile>${dist_path}/${dist_name}.exe</outfile>
    <jar>${build_temp_dir}/main.jar</jar>
    <errTitle>${dist_name}</errTitle>
    <chdir>.</chdir>
    <customProcName>true</customProcName>
    % if ico:
    <icon>${ico}</icon>
    % endif
    <classPath>
        <mainClass>${main_class}</mainClass>
        <cp>lib/jython.jar</cp>
        <cp>lib/jython-lib.jar</cp>
        % for classpath in classpaths:
        <cp>${classpath}</cp>
        % endfor
    </classPath>
    <jre>
        <minVersion>1.4.0</minVersion>
    </jre>
    <!-- <splash>
        <file>path/filename.png</file>
        <waitForWindow>true</waitForWindow>
        <timeout>60</timeout>
        <timeoutErr>true</timeoutErr>
    </splash> -->
    <!-- <versionInfo>
        <fileVersion></fileVersion>
        <txtFileVersion></txtFileVersion>
        <fileDescription></fileDescription>
        <copyright></copyright>
        <productVersion></productVersion>
        <txtProductVersion></txtProductVersion>
        <productName></productName>
        <companyName></companyName>
        <internalName></internalName>
        <originalFilename></originalFilename>
      </versionInfo> -->
</launch4jConfig>
