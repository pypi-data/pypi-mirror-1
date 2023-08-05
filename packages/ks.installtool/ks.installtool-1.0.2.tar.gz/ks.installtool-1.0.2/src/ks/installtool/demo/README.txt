$Id$

Что удалось выяснить про создание форм:

    Некоторые проблемы мы разрулим потом. На
    момент сейчас известно, что бы создать
    форму вызова фабрики и поместить ее в контекстное
    меню надо::
    
      <install
          name="demo"
          root="zope.app.folder.folder.Folder"
          >
          <property name="par1" value="11"/>
          <property name="par2" value="12"/>
          <property name="par2" value="12"/>
          <property name="par4" value="14"/>
      </install> 
     
    Вызвать zope:install, что бы создать и зарегестрировать
    фабрику, здесь:
    
        name -- имя фабрики (уникальное), фабрика
            создается как класс в модуле installtool.factories
            под этим именем,
            
        root -- корневой объект процедуры инсталляции: вначале
            создается и добавляется он, а затем все остальное.
            
    Будем называть:
    
        имя фабрики -- имя, указанное в name (demo),
        
        полное имя фабрики -- имя, указанное вместе с модулем 
            (installtool.factories.demo).
    
    Вызвать директиву zope:class, что бы дать права использовать
    интерфейс zope.component.interfaces.IFactory для созданной
    фабрики. В поле class указывается полное имя фабрики: 

       <class class="installtool.factories.demo">
          <require interface="zope.component.interfaces.IFactory" permission="zope.ManageContent" />
       </class>


    Вызвать директиву browser:addform, что бы создать форму добавления:

      <browser:addform
          name="calldemo.html"
          content_factory_id="installtool.factories.demo"
          class=".add.AddMixIn"
          schema=".interfaces.IDemo"
          permission="zope.ManageContent"
          keyword_arguments="title body"
          for="*"
        />
    
    Здесь:
    
        name -- имя формы добавления, нужно указывать обязательно,
        
        content_factory_id -- указывается полное имя фабрики,
        
        class -- всегда указывается класс .add.AddMixIn,
        
        schema -- указывается схема для генерации формы,
        
        permission -- разрешение на вызов формы, должно совпадать
            с разрешением, указанным в директиве class,
            
        keyword_arguments -- должны быть перечислены все аргументы
            схемы, иначе созданный контент-класс попытаются
            привести к интерфейсу схемы, что в общем случае
            невозможно, этот атрибут можно сгенерировать
            по схеме,
            
        for -- указывается интерфейс, для которого отображается
            форма вызова фабрики,


    Вызвать директиву browser:addMenuItem, что бы добавить форму в меню:
    
      <browser:addMenuItem
          factory="installtool.factories.demo"  
          view="calldemo.html"
          title="Demo"
          description="Demo Demo"
          permission="zope.ManageContent"
          />  
    
        Здесь:
        
            factory -- полный путь к фабрике,
            
            view -- название вида (name из browser:addform), указывать
                обязательно, иначе фабрика будет вызываться без вида
                и скрипты не будут вызываться,
                
            title -- название п. меню,
            
            description -- описание формы,
            
            permission -- разрешения отображать п. меню, совпадает с предыдущими
                двумя.
                
    Очевидно, работу по созданию фабрики можно сильно упростить, если
    создать директиву factoryform, объединяющую в себе все четыре директивы.
    
    За начальное приближение лучше взять директиву install, от ее хендлера
    породить свою и добавить все необходимые атрибуты. В конце вызвать
    кроме хендлера utility хендлеры остальных трех директив.
       